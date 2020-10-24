D			[0-9]
L			[a-zA-Z_]
H			[a-fA-F0-9]
W			[ \t\v\n\f]
S			L?\"(\\.|[^\\"])*\"
C1			(\/\/)+[^\n]*
C2			"/*"([^*]|("*")+[^/*])*("*")+"/"
I			#include{W}+{S}
D1			INFO[^\n]*
D3			ERR[^\n]*
D2			WARN[^\n]*


%{
#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <string.h>
#include <windows.h>
#include "base64.h"
#include "utils.h"
#include "list.h"

typedef struct OPTIONS {
	char makeBackup;
	char key;
	char decFunc[64];
	list* includedDirs;
	list* files;
} options, *poptions;

DATA_BLOB* enc, *s;
FILE* log;
long count, total;

options opt;
%}

%%
"auto"					{ return(ECHO); }
"break"					{ return(ECHO); }
"case"					{ return(ECHO); }
"char"					{ return(ECHO); }
"const"					{ return(ECHO); }
"continue"				{ return(ECHO); }
"default"				{ return(ECHO); }
"do"					{ return(ECHO); }
"double"				{ return(ECHO); }
"else"					{ return(ECHO); }
"enum"					{ return(ECHO); }
"extern"				{ return(ECHO); }
"float"					{ return(ECHO); }
"for"					{ return(ECHO); }
"goto"					{ return(ECHO); }
"if"					{ return(ECHO); }
"inline"				{ return(ECHO); }
"int"					{ return(ECHO); }
"long"					{ return(ECHO); }
"register"				{ return(ECHO); }
"restrict"				{ return(ECHO); }
"return"				{ return(ECHO); }
"short"					{ return(ECHO); }
"signed"				{ return(ECHO); }
"sizeof"				{ return(ECHO); }
"static"				{ return(ECHO); }
"struct"				{ return(ECHO); }
"switch"				{ return(ECHO); }
"typedef"				{ return(ECHO); }
"union"					{ return(ECHO); }
"unsigned"				{ return(ECHO); }
"void"					{ return(ECHO); }
"volatile"				{ return(ECHO); }
"while"					{ return(ECHO); }
"_Alignas"              { return ECHO; }
"_Alignof"              { return ECHO; }
"_Atomic"               { return ECHO; }
"_Bool"                 { return ECHO; }
"_Complex"              { return ECHO; }
"_Generic"              { return ECHO; }
"_Imaginary"            { return ECHO; }
"_Noreturn"             { return ECHO; }
"_Static_assert"        { return ECHO; }
"_Thread_local"         { return ECHO; }
"__func__"              { return ECHO; }
{I}									{ ECHO; }
{C1}								{ ECHO; }
{C2}							 	{ ECHO; }
{D1}								{ ECHO; }
{D3}								{ ECHO; }
{D2}								{ ECHO; }
{S}									{ s = createDataBlobFromString(yytext, 1, 1);
                                      processEscapeChar(s);	
                                      fprintf(log, "\t%s |%s | ", yytext, s->pbData);
                                      cipher(s, opt.key);
                                      enc = encode64(s);
									  fprintf(log, "%s\n", enc->pbData);
									  count++;
                                      fprintf(yyout, "%s(\"%s\")", opt.decFunc, enc->pbData);
                                      freeDataBlob(enc);
                                      freeDataBlob(s);
                                    }
{W}									{ ECHO; }
.									{ ECHO; }

%%


void usage() {
    char* exe = "StringCrypter.exe";
    printf("\nUsage : %s [-h] [--config file (\"sc.ini\")]\n", exe);
    exit(0);
}

void cryptFile(char* file, char* shortfile){
	char bak[MAX_PATH];
	strcpy(bak, file);
	bak[strlen(bak)-2] = '\0';
	sprintf(bak, "%s.bak", bak);
    if (file && fileExists(file)) {
		printf("    %-16s", shortfile);
		CopyFile(file, bak, 0);
        yyin = fopen(bak, "r");
        yyout = fopen(file, "w");

		count = 0;
	    yylex();
		printf("%5d\n", count);
		total += count;
		
        fclose(yyin);
        fclose(yyout);
		if (!opt.makeBackup) DeleteFile(bak); 
    }else{
		printf("    Unable to open file : %s\n", file);
	}
}

void revertFile(char* file, char* shortfile){
	char bak[MAX_PATH];
	strcpy(bak, file);
	bak[strlen(bak)-2] = '\0';
	sprintf(bak, "%s.bak", bak);
	if (fileExists(bak)){
		printf("    Reverting file : %s\n", shortfile);
		MoveFileEx(bak, file, MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH);
	}else{
		printf("    Unable to revert file : %s (No backup found)\n", shortfile);
	}
}

void readConfig(char* conf){
	FILE* f = fopen(conf, "r");
	char info[1024];
	char line[4096];
	char* tmp;
	int i;

	strcpy(opt.decFunc, "decStr");
	opt.includedDirs = listCreate();
	opt.files = listCreate();
	opt.key = 0;
	opt.makeBackup = 1;

	if (f){
		printf("Reading config file ...\n");
		while (!feof(f)){
			memset(info, 0, 24);
			fscanf(f, "%s = ", info);
			if (strcmp(info, "key")==0){
				fscanf(f, "%d", &i);
				opt.key = i;
				printf("    Key : %d\n", i);
			}else if (strcmp(info, "decryptFunctionName")==0){
				fscanf(f, "%s", opt.decFunc);
				printf("    Decrypt function name : %s\n", opt.decFunc);
			}else if (strcmp(info, "makeBackup")==0){
				fscanf(f, "%d", &i);
				opt.makeBackup = i;
				printf("    makeBackup : %d\n", i);
			}else if (strcmp(info, "files")==0){
				//printf("    files :\n");
				memset(line, 0, 4096);
				fgets(line, 4096, f);
				tmp = strtok(line, ":;\n");
				while (tmp){
					listAdd(opt.files, strdup(tmp));
					//printf("        %s\n", tmp);
					tmp = strtok(NULL, ";:\n");
				}
			}else if (strcmp(info, "includes")==0){
				//printf("    includes :\n");
				memset(line, 0, 4096);
				fgets(line, 4096, f);
				tmp = strtok(line, ";:\n");
				while (tmp){
					listAdd(opt.includedDirs, strdup(tmp));
					//printf("        %s\n", tmp);
					tmp = strtok(NULL, ";:\n");
				}
			}
		}
		fclose(f);
		printf("Reading config file terminated\n");
	}else{
		printf("Unable to find config file\n");
		exit(0);
	}
}

int main(int argc, char** argv){
    int help = 0, revert = 0;
    char *currentFile, *config = "sc.ini";
	char buffer[MAX_PATH];
	FILE* header, *code;

	list* fileListTmp, *includedDirsTmp;
    int i;

	GetCurrentDirectory(256, buffer);
	printf("%s\n", buffer);

    for(i=1; i<argc; i++){
        if       (strcmp(argv[i], "-h")==0){
            help = 1;
        }else if (strcmp(argv[i], "--config")==0){
            config = argv[++i];
        }else if (strcmp(argv[i], "--revert")==0){
            revert = 1;
        }else{
            fprintf(stderr, "Unknown options : %s\n", argv[i]);
			help = 1;
        }
    }

    if (help) usage();
    
	readConfig(config);

    if (!opt.key) printf("Info : Default Key (0x00) will be used\n");
    if (strcmp(opt.decFunc, "decStr")==0) printf("Info : Default decryption's function name (\"decStr\") will be used\n");
	if (!revert && !opt.makeBackup){
		printf("Warning : MakeBackup options is not set, restoring file will not be possible !\nContinue (y/n) ? ");
		scanf("%s", buffer);
		if (buffer[0] == 'n') exit(0);
	}

	log = fopen("StringCrypter.log", "w");
	total = 0;

	printf("Processing files ...\n");
    if (!listIsEmpty(opt.files)){
		fileListTmp = opt.files;
		while (fileListTmp){
			currentFile = NULL;
			if (fileExists(fileListTmp->data)) currentFile = fileListTmp->data;
			else{
				if (!listIsEmpty(opt.includedDirs)){
					includedDirsTmp = opt.includedDirs;
					while (includedDirsTmp){
						sprintf(buffer, "%s\\%s", includedDirsTmp->data, fileListTmp->data);
						if (fileExists(buffer)){
							currentFile = buffer;
							break;
						}
						includedDirsTmp = includedDirsTmp->next;
					}
				}
			}
			if (currentFile){
				if (revert) revertFile(currentFile, fileListTmp->data);
				else cryptFile(currentFile, fileListTmp->data);
			}else
				printf("    Unable to find : %s\n", fileListTmp->data);

			fileListTmp = fileListTmp->next;
		}
	}
	printf("Processing files terminated\n");

	printf("\n    %d string encrypted\n", total);
	fclose(log);
       
    return 0;
}
    
#include <stdio.h>
#include <string.h>
#include <math.h>

double count[256];

double computeEntropy(double size) {
	double ent = 0;
	long i;
	for (i = 0; i < 256; i++) {
		if (count[i]) {
			count[i] /= size;
			ent -= (count[i] * (log10l(count[i]) / log10l(256)));
		}
	}
	return ent;
}

int main(int argc, char** argv) {
	FILE* inf = NULL;
	char* inb = NULL;
	size_t size = 0;

	if (argc > 1)
	{
		errno_t err = fopen_s(&inf, argv[1], "rb");
		if (err) {
			inb = _strdup(argv[1]);
			size = strlen(inb);
			inf = NULL;
		}
		else if (inf)
		{
			fseek(inf, 0, SEEK_END);
			size = ftell(inf);
			fseek(inf, 0, SEEK_SET);
		}

		memset(count, 0, 256 * sizeof(double));

		if (!inf) {
			for (unsigned long i = 0; i < size; i++)
			{
				count[inb[i]]++;
			}
		}
		else {
			while (!feof(inf))
			{
				count[fgetc(inf) & 0xff]++;
			}
		}

		printf("%0.2f", computeEntropy(size));
	}

	return 0;
}
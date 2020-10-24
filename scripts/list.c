#include <list.h>
#include <stdlib.h>

list* listCreate(){
	list* l = (list*)malloc(sizeof(listitem));
	l->prev = NULL;
	l->next = NULL;
	l->data = NULL;
	return l;
}

int listIsEmpty(list* l){
	return ((l->data == NULL) && (l->next == NULL) && (l->prev == NULL));
}

listitem* listAdd(list* l, char* data){
	listitem* item = NULL;
	listitem* insertPos;
	if (listIsEmpty(l)){
		l->data = data;
	}else{
		item = (listitem*)malloc(sizeof(listitem));
		item->data = data;
		item->next = NULL;
		insertPos = l;
		while (insertPos->next != NULL){
			insertPos = insertPos->next;
		}
		insertPos->next = item;
		item->prev = insertPos->next;
	}
	return item;
}

listitem* listRemove(list* l, listitem* item){
	listitem* tmp = item;
	if (!listIsEmpty(l)){
		if (item->prev != NULL){
			item->prev->next = item->next;
		}
		free(tmp->data);
		free(tmp);
	}
	return l;

}

void listFree(list* l){
	listitem* tmp;
	if (l != NULL){
	while (l->prev != NULL) l = l->prev;
	while (l != NULL){
		tmp = l;
		l = l->next;
		free(tmp->data);
		free(tmp);
	}
	}
}

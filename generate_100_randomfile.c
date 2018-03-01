#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <sys/wait.h>
#include <stdlib.h>

//xterm -hold -e dstring proccess.txt

char* concat(const char *s1, const char *s2)
{
    char *result = malloc(strlen(s1)+strlen(s2)+1);//+1 for the null-terminator
    //in real code you would check for errors in malloc here
    strcpy(result, s1);
    strcat(result, s2);
    return result;
}
int main(int argc, char *argv[])
{
    char buf;
//    char *s = malloc(sizeof(1000));
//    size_t n;

    if(argc != 2) {
        fprintf(stderr, "Usage : %s <String>\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    char s1[] = "xterm -hold -e dstring ";
    char *str = strcat(s1,argv[1]);
//    system("xterm -hold -e dstring " argv[1]);
    //printf("%s",str);
    system(str);
    exit(EXIT_SUCCESS);


}


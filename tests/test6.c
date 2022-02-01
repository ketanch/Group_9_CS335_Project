// File I/O
int main(){
    FILE *x;
    char buff[100];

    x=fopen("/tests/test4.c","w+");
    fscanf("%s",&buff);
    printf("%s",buff);
    fprintf(fp,"Adding to file");
    fclose(fp);
    return 0;
}
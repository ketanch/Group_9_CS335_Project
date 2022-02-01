// functions
void tmpf(int a){
    printf("%d",a);
    return;
}
int main(){
    int a=34;
    tmpf(a);
    goto afterFunction;
    afterFunction:
        printf("Function execution completed");
    return 0;
}
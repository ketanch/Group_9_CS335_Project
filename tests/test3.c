// if else and loops
#define M 4
int main()
{
    int k;
    k = k + 4 - 5 * 5.4e4 / 45 % 3;
    if (k == 4 && k <= 6)
        printf("hello");
    else
        printf("hi");
    for(int i=-2;i<10;i++){
        if(i<0){
            i++;
            continue;
        }
        if(i>7){
            break;
        }
        printf("%d",i);
    }
    int x=35;
    while(x--){
        printf("%d",x);
    }
    do{
        printf("%d",++x);
    }while(x<10);
    return 0;
}
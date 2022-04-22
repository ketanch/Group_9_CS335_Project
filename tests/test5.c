int main(){
    int a = 1, b=5;
    
    if (!printf("1") && printf("2")){
        ;
    }
    if(printf("3") || printf("4")){
        ;
    }

    if(a || b++){
        printf( a);
        printf(b);
    }
    printf( a);
    printf(b);
    a=0;
    b=3;
    if(a++ && --b){
        printf( a);
        printf(b);
    }
    printf( a);
    printf(b);
    return 0;
}

int main()
{
    int a = 1;
    int *b = &a;
    printf("Value of a = ");
    printf(a);
    printf("\nValue at address stored in b = ");
    int t = *b;
    printf(t);
    a = 2;
    printf("\nNew Value of a = ");
    printf(a);
    t = *b;
    printf("\nValue at address stored in b = ");
    printf(t);
}
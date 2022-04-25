// struct point {
//     int x;
//     int y;
// };
// int main()
// {
//     struct point a;
//     a.x = 1;
//     a.y = 2;

//     printf("Struct Variable 'a' consists of x and y attributes. \n");
//     int t = a.x;
//     printf(t);
//     t = a.y;
//     printf(" ");
//     printf(t);
// }

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
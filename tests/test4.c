int main()
{
    int i = 0;
    printf("Linearly Increasing For Loop\n");
    for ( i = 1 ; i < 10 ; i++ )
    {
        printf("i = ");
        printf(i);
        printf("\n");
    }
    printf("Exponentially Increasing For Loop\n");
    for ( i = 1 ; i <= 100 ; i = i * 2 )
    {
        printf("i = ");
        printf(i);
        printf("\n");
    }
    printf("Linearly Decreasing For Loop\n");
    for ( i = 9 ; i >= 0 ; i-- )
    {
        printf("i = ");
        printf(i);
        printf("\n");
    }
    printf("While Loop\n");
    i = 0 ;
    while ( i < 10 )
    {
        printf("i = ");
        printf(i);
        printf("\n");
        i++;
    }
    printf("Do While Loop\n");
    i = 0 ;
    do
    {
        printf("i = ");
        printf(i);
        printf("\n");
        i++;
    } while ( i < 10 );
}
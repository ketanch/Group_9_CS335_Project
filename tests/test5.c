int main()
{
    int a[10];
    int i;
    for( i = 0 ; i < 10 ; i ++ )
    {
        a[i] = i;
    }
    for( i = 0 ; i < 10 ; i ++ )
    {
        int t = a[i];
        printf("a[");
        printf(i);
        printf("] = ");
        printf(t);
        printf(" \n");
    }
}

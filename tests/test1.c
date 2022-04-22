int rec(int m , int n)
{
    if(m == 0)
        return n+1 ;
    
    if(n == 0)
    {
        return rec(m-1 , 1) ;
    }

    return rec(m-1 , rec(m , n-1)) ;
}
int main()
{   
    int i , j ;
    for(i = 0 ; i < 4 ; i++)
    {
        for(j = 0 ; j < 4 ; j++)
            printf(i);
            printf(j);
            int tmp=rec(i,j);
            printf(tmp);
    }
    return 0 ;
}
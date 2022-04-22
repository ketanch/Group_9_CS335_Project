void binary_search(int arr[] , int l , int r , int val)
{   
    int mid ;
    printf(l);
    printf(r);
    if(l > r)
    {
        return ;
    }
    mid = (l+r)/2 ;
    if(arr[0] == val)
    {
        printf(mid) ;
        return ;
    }
    if(arr[0] > val)
        return binary_search(arr , l , mid-1 , val) ;
    return binary_search(arr , mid+1 , r , val) ;
}
int main()
{
    int arr[500] ;
    int i = 0 ; 
    binary_search(arr , 0 , 499 , 147) ;
    binary_search(arr , 0 , 499 , 700) ;
    binary_search(arr , 0 , 499 , 0) ;
    return 0 ;
}
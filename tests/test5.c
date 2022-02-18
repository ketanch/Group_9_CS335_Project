// I/O checks
int main(){
    int x=0;
    x++;
    float f=34.56;
    switch(x){    
        case 0:    
        f=0;  
        break;    
        case 1:    
        f=10000;
        break;    
        case -1:    
        f=-10000;
        break;    
        default:    
        f=0;
    }    
    return 0;
}
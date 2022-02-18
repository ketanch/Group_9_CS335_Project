//Data type check
#define INT_MAX 1000000000 
int main(){
    short int si=-110;
    unsigned short int usi=10;
    int i=-33233;
    unsigned int ui=484;
    long int li=-INT_MAX;
    long unsigned int uli=7493;
    long long int lli=-19932;
    long long unsigned int ulli=749993;
    float f=12.34;
    double d=-233.444;
    const int ci=4884;
    bool bt=true;
    bool bf=false;
    char c='a';
    unsigned char uc='d';
    int *ptr=&i;
    struct st{
        int a;
        float sf;
    };
    union u{
        int ui;
        float uf;
    };
    return 0;
}
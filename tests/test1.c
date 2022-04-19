int func(int a,int b){
    a=43;
}
int main() {
    int a;
    int n = 4;
    int g = 9;
    a = (n+g) * (n*g);
    func(a);
}
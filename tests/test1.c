// int main() {
//     int a[5];
//     a[4] = 5;
//     //a[5] = 6;
//     struct point {
//         int x;int y;
//     };
//     //struct point p;
//     //p.y = 8;
//     //struct point *q;
//     //q->y=5;
//     //int r;
//     //int *s = &r;
//     //*s = 5;
//     int tt = a[4];
//     printf(tt);
// }

int main() {
    int a = 5; 
    int b = 4;
    //int c = a+b;
    int c = a++ + ++b + a*b + b*b;
    printf(c);
}
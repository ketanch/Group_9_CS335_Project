int main() {
    int a[5];
    a[4] = 19;
    a[5] = 6;
    struct point {
        int x;int y;
    };
    //struct point p;
    //p.y = 8;
    //struct point *q;
    //q->y=5;
    int r;
    int *s = &r;
    *s = 0x69;
    int tt = r; //p.y;
    printf(tt);
    printf("\n");
    printf(r);
}
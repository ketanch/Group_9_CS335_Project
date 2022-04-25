int func(int s) {
    printf("Func called\n");
    return 5;
}

int main() {
    int i = 0;
    int a[5];
    while (i < 5) {
        a[i] = i;
        i++;
    }
    for (i=0;i<5;i++) {
        int t = a[i];
        printf(t);
        printf("\n");
    }
    func(4);
    printf(a);
}
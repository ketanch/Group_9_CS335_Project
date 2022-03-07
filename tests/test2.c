#define M 4
int main()
{
    int k=6;
    k = 2;
    k &= 4, k -= 4;
    k *= 4;
    k /= 4;
    k %= 4;
    k <<= 4;
    k >>= 4;
    k &= 4;
    k |= 4;
    k ^= 4;
    return 0;
}
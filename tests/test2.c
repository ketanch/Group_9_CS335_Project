#define M 4
int main()
{
    int k;
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
}
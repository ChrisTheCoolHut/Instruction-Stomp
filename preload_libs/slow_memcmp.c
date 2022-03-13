#include <string.h>

int memcmp(const void *s1, const void *s2, size_t n)
{
	int i =0;
	char * ptr = s1;
	char * pt2 = s2;
	for(i=0; i< n;i++)
	{
		if (ptr[i] != pt2[i]) return -1;
	}
	return 0;
}
#include <stdio.h>
#include <stdlib.h>

void CountingSort(int A[], int n) {
    int min = A[0], max = A[0];
    for (int i = 1; i < n; i++) {
        if (A[i] < min){
            min = A[i];
        }
        if (A[i] > max){
            max = A[i];
        }
    }
    int range = max - min + 1;
    int *C = (int *)calloc(range, sizeof(int));
    int *B = (int *)malloc(n * sizeof(int));
    for (int i = 0; i < n; i++) {
        C[A[i] - min]++;
    }
    for (int i = 1; i < range; i++) {
        C[i] += C[i - 1];
    }
    for (int i = n - 1; i >= 0; i--) {
        B[C[A[i] - min] - 1] = A[i];
        C[A[i] - min]--;
    }
    for (int i = 0; i < n; i++) {
        A[i] = B[i];
    }
    free(C);
    free(B);
}
void Array(int A[], int n) {
    for (int i = 0; i < n; i++) {
        printf("%d ", A[i]);
    }
    printf("\n");
}
int main() {
    int n;
    printf("Enter number of elements: ");
    scanf("%d", &n);
    int *arr = (int *)malloc(n * sizeof(int));
    printf("Enter %d integers:\n", n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    printf("\nArray before sorting: ");
    printArray(arr, n);
    countingSort(arr, n);
    printf("Array after sorting: ");
    printArray(arr, n);
    free(arr);
    return 0;
}
def fibonacci(n):
    a, b = 0, 1
    if n <= 0:
        print("Please enter a positive integer")
    elif n == 1:
        print(a)
    else:
        print("Fibonacci sequence:")
        for i in range(n):
            print(a)
            a, b = b, a + b

num_terms = int(input("Enter the number of terms: "))
fibonacci(num_terms)
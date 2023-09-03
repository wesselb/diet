from diet import nutrients, print_table

if __name__ == "__main__":
    max_key_length = max(map(len, nutrients.keys()))
    print_table(sorted(nutrients.items(), key=lambda x: x[0]))

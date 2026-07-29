from f import append_to_file, id_generator

lids = [id_generator() for _ in range(6400)]


for lid in lids:
    append_to_file("lids.txt", f"{lid}\n")

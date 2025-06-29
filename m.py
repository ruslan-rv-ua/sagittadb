from sagitta import Sagitta

db = Sagitta(":memory:")
# db.insert({"key": "value"})
db.insert("not a dict")
# db.insert([1, 2, 3])
db.insert_many([{"key1": "value1"}, {"key2": "value2"}, "just a string"])
db.insert({"key1": "value1", "key2": "value2"})

print(list(db.all()))

print()
a = db.search(
    {"key1": "value1"}
    # {"key1": "new_value1", "key2": "new_value2", "key3": "new_value3"},
    # {"key1": "new_value1", "key2": "new_value2"},
)

print(list(db.all()))
print(list(a))

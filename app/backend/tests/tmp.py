def test_list_looping(list_to_look_in):
    little_nice = ["yaya", "yaya5", "lalalala"]
    for name in little_nice:
        if name in list_to_look_in:
            print(name)


look_up_list = ["yaya", "yaya2", "yaya4", "yaya5"]
test_list_looping(look_up_list)
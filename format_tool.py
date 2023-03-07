import texttable


def format_print_course(course_json):
    table = texttable.Texttable()
    table.set_cols_align(['r', 'c', 'c', 'c'])
    table.set_deco(texttable.Texttable.BORDER | texttable.Texttable.HEADER)
    title = ['课程id', '课程名', '课程人数', '课程状态']
    rows = []
    for item in course_json['content']:
        if item['selected'] is True:
            status = "已选择"
        else:
            status = "未选择"
        rows.append([item['id'],
                     item['courseName'],
                     f"{item['courseCurrentCount']}/{item['courseMaxCount']}",
                     status])
    table.add_rows([title, *rows])
    print(table.draw())

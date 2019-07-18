# coding: utf8
import collections


class ParseTable(object):

    def __init__(self, file_path="db.sql"):
        table_name = ""
        primary_key_list = []
        column_type_list = list()
        with open(file_path) as f:
            for line in f:
                line = line.strip().lower()
                if not line:
                    continue
                if line.find("engine") >= 0 or line.find("database") >= 0:
                    continue
                if line.find("create table") >= 0:
                    line = line.replace("create table", "")
                    line = line.replace("(", "")
                    line = line.strip()
                    line = line.strip("\`")
                    table_name = line
                elif line.find("primary key") >= 0:
                    line = line.replace("primary key", "")
                    line = line.strip()
                    line = line.strip(",")
                    line = line.strip("(")
                    line = line.strip(")")
                    primary_key_item = line.split(",")
                    for item in primary_key_item:
                        item = item.strip()
                        item = item.strip("`")
                        primary_key_list.append(item)
                elif line.find("int") >= 0 or line.find("char") >= 0 or line.find("text") >= 0 or line.find(
                        "timestamp"):
                    column_info = line.split(" ")
                    column = column_info[0].strip().strip("`")
                    column_type_list.append((column, column_info[1]))
        self.table_name = table_name
        self.primary_key_list = primary_key_list
        self.column_type_list = column_type_list

    @staticmethod
    def convert_to_hump(string):
        items = string.split("_")
        ret = "".join(["{}{}".format(item[0].upper(), item[1:]) for item in items])
        return ret

    @staticmethod
    def convert_to_hump_variable(string):
        items = string.split("_")
        ret = "".join(["{}{}".format(item[0].upper(), item[1:]) for item in items])
        ret = ret[0].lower() + ret[1:]
        return ret

    @staticmethod
    def mysql_type_to_go_type(mysql_type):
        column_type = "int32"
        if mysql_type.find("bigint") >= 0:
            column_type = "int64"
        elif mysql_type.find("char") >= 0 or column_type.find("text") >= 0:
            column_type = "string"
        elif mysql_type.find("timestamp") >= 0:
            column_type = "time.Time"
        return column_type

    def generate_column_str(self, column, mysql_type, primary_key_mark):
        primary_str = ""
        timestamp_str = ""
        if primary_key_mark:
            primary_str = ";primary_key"
        column_type = "int32"
        if mysql_type.find("bigint") >= 0:
            column_type = "int64"
        elif mysql_type.find("char") >= 0 or mysql_type.find("text") >= 0:
            column_type = "string"
        elif mysql_type.find("timestamp") >= 0:
            column_type = "time.Time"
            timestamp_str = '''sql:"DEFAULT:current_timestamp"'''
        ret = '''    %s  %s  `gorm:"column:%s;type:%s%s" %s json:"%s"`\n''' % (
        self.convert_to_hump(column), column_type, column,
        mysql_type, primary_str, timestamp_str, column)
        return ret

    def generate_attr_str(self, column, mysql_type):
        column_type = "int32"
        if mysql_type.find("bigint") >= 0:
            column_type = "int64"
        elif mysql_type.find("char") >= 0 or column_type.find("text") >= 0:
            column_type = "string"
        elif mysql_type.find("timestamp") >= 0:
            column_type = "time.Time"
        ret = '''    %s  %s  `json:"%s"`\n''' % (self.convert_to_hump(column), column_type, column)
        return ret

    def generate_struct(self):
        ret_str = ""
        ret_str += '''type %sRet struct {\n''' % self.convert_to_hump(self.table_name)
        primary_key_mark_map = collections.defaultdict(bool)
        for k, _ in self.column_type_list:
            if k in self.primary_key_list and len(self.primary_key_list) == 1:
                primary_key_mark_map[k] = True
        for k, v in self.column_type_list:
            ret_str += self.generate_attr_str(k, v)
        ret_str += "}\n"
        return ret_str

    def generate_table_struct(self):
        ret_str = ""
        ret_str += '''type %s struct {\n''' % self.convert_to_hump(self.table_name)
        primary_key_mark_map = collections.defaultdict(bool)
        for k, _ in self.column_type_list:
            if k in self.primary_key_list and len(self.primary_key_list) == 1:
                primary_key_mark_map[k] = True
        for k, v in self.column_type_list:
            ret_str += self.generate_column_str(k, v, primary_key_mark_map[k])
        ret_str += "}\n"
        return ret_str

    def generate_table_name_function(self):
        ret_str = ""
        ret_str += '''func (%s) TableName() string {\n    return "%s"\n}\n''' % (self.convert_to_hump(self.table_name),
                                                                                 self.table_name)
        return ret_str

    def generate_create_table_function(self):
        primary_key = self.primary_key_list[0]
        for item in self.column_type_list:
            if item[0] == primary_key:
                mysql_type = item[1]
        ret = ""
        ret += '''func(item %s) Create()(err error, %s %s) {\n    ret := DbConnection.Create(&item)\n    err = ret.Error\n    %s = item.%s\n    return\n}\n''' % (
        self.convert_to_hump(self.table_name),
        self.convert_to_hump_variable(primary_key), self.mysql_type_to_go_type(mysql_type), self.convert_to_hump_variable(primary_key),
        self.convert_to_hump(primary_key))
        return ret

    def generate_update_table_function(self):
        ret = '''func (item %s) Update() (err error) {\n    ret := DbConnection.Save(&item)\n    err = ret.Error\n    return\n}\n'''
        return ret % (self.convert_to_hump(self.table_name))

    def generate_list_function(self):
        ret = '''func Query%sList(offset int32, size int32) (item []%s) {\n    DbConnection.Offset(offset).Limit(size).Find(&item)\n    return\n}\n''' % (
        self.convert_to_hump(self.table_name), self.convert_to_hump(self.table_name))
        return ret

    def generate_total_function(self):
        ret = '''func Query%sCount() (count int64) {\n    DbConnection.Model(%s{}).Count(&count)\n    return\n}\n''' % (
        self.convert_to_hump(self.table_name), self.convert_to_hump(self.table_name))
        return ret

    def generate_query_by_primary_key_function(self):
        primary_key = self.primary_key_list[0]
        ret = '''func Query%sBy%s(%s int64) (item %s) {\n    DbConnection.Where("%s=?", %s).First(&item)\n    return\n}\n'''
        ret = ret % (self.convert_to_hump(self.table_name), self.convert_to_hump(primary_key), self.convert_to_hump_variable(primary_key),
                     self.convert_to_hump(self.table_name), primary_key, self.convert_to_hump_variable(primary_key))
        return ret

    def generate_update_column_function(self):
        ret = '''func (item %s) UpdateColumns() (error, int64) {\n    updateMap := make(map[string]interface{})\n''' % self.convert_to_hump(
            self.table_name)
        for item in self.column_type_list:
            if item[0] not in self.primary_key_list:
                if item[1].find("timestamp") >= 0:
                    continue
                null_value = 0
                if item[1].find("char") >= 0 or item[1].find("text") >= 0:
                    null_value = '""'
                ret += '''    if item.%s != %s {\n        updateMap["%s"] = item.%s\n    }\n''' % (
                self.convert_to_hump(item[0]), null_value, item[0], self.convert_to_hump(item[0]))
        ret += '''    ret := DbConnection.Model(%s{}).Where("%s=?", item.%s).Updates(updateMap)\n    return ret.Error, ret.RowsAffected\n}\n''' % \
               (self.convert_to_hump(self.table_name), self.primary_key_list[0], self.convert_to_hump(self.primary_key_list[0]))
        return ret

    def generate_go_file(self):
        wf = open("modules/%s_mysql_op.go" % self.table_name, "w")
        wf.write('''package modules\n\nimport (\n    "time"\n)\n''')
        wf.write("\n")
        wf.write(self.generate_struct())
        wf.write("\n")
        wf.write(self.generate_table_struct())
        wf.write("\n")
        wf.write(self.generate_table_name_function())
        wf.write("\n")
        wf.write(self.generate_create_table_function())
        wf.write("\n")
        wf.write(self.generate_update_column_function())
        wf.write("\n")
        wf.write(self.generate_update_table_function())
        wf.write("\n")
        wf.write(self.generate_list_function())
        wf.write("\n")
        wf.write(self.generate_total_function())
        wf.write("\n")
        wf.write(self.generate_query_by_primary_key_function())


if __name__ == "__main__":
     db = ParseTable("db.sql")
     db.generate_go_file()
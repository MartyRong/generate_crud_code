package main

import (
	"generate_crud_code/modules"
	"fmt"
)

func main()  {
	modules.InitConnection()
	var item modules.Student
	item.Name = "张三"
	item.Grade = 3
	item.Age = 9
	item.OrderNumber = 1
	item.Gender = "男"
	item.Description = "三好学生"
	_, id := item.Create()
	fmt.Printf("Id: %d\n", id)

	student := modules.QueryStudentById(id)
	fmt.Printf("student:%v\n", student)

}

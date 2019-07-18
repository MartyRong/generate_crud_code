package modules

import (
	"fmt"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/mysql"
)

var (
	DbConnection *gorm.DB
)

func InitConnection() {
	var err error
	db, err := gorm.Open("mysql", "root:test123@tcp(127.0.0.1:3306)/school?charset=utf8mb4&parseTime=True&loc=Local")
	if err != nil {
		panic(err)
	}
	fmt.Printf("数据库连接成功!\n")
	DbConnection = db
}
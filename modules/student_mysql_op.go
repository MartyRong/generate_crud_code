package modules

import (
	"time"
)

type StudentRet struct {
	Id          int64     `json:"id"`
	Name        string    `json:"name"`
	Gender      string    `json:"gender"`
	Age         int32     `json:"age"`
	Grade       int32     `json:"grade"`
	OrderNumber int64     `json:"order_number"`
	Description int32     `json:"description"`
	UpdateTime  time.Time `json:"update_time"`
}

type Student struct {
	Id          int64     `gorm:"column:id;type:bigint(20);primary_key"  json:"id"`
	Name        string    `gorm:"column:name;type:varchar(100)"  json:"name"`
	Gender      string    `gorm:"column:gender;type:varchar(32)"  json:"gender"`
	Age         int32     `gorm:"column:age;type:int(11)"  json:"age"`
	Grade       int32     `gorm:"column:grade;type:tinyint(4)"  json:"grade"`
	OrderNumber int64     `gorm:"column:order_number;type:bigint(20)"  json:"order_number"`
	Description string    `gorm:"column:description;type:text"  json:"description"`
	UpdateTime  time.Time `gorm:"column:update_time;type:timestamp" sql:"DEFAULT:current_timestamp" json:"update_time"`
}

func (Student) TableName() string {
	return "student"
}

func (item Student) Create() (err error, id int64) {
	ret := DbConnection.Create(&item)
	err = ret.Error
	id = item.Id
	return
}

func (item Student) UpdateColumns() (error, int64) {
	updateMap := make(map[string]interface{})
	if item.Name != "" {
		updateMap["name"] = item.Name
	}
	if item.Gender != "" {
		updateMap["gender"] = item.Gender
	}
	if item.Age != 0 {
		updateMap["age"] = item.Age
	}
	if item.Grade != 0 {
		updateMap["grade"] = item.Grade
	}
	if item.OrderNumber != 0 {
		updateMap["order_number"] = item.OrderNumber
	}
	if item.Description != "" {
		updateMap["description"] = item.Description
	}
	ret := DbConnection.Model(Student{}).Where("id=?", item.Id).Updates(updateMap)
	return ret.Error, ret.RowsAffected
}

func (item Student) Update() (err error) {
	ret := DbConnection.Save(&item)
	err = ret.Error
	return
}

func QueryStudentList(offset int32, size int32) (item []Student) {
	DbConnection.Offset(offset).Limit(size).Find(&item)
	return
}

func QueryStudentCount() (count int64) {
	DbConnection.Model(Student{}).Count(&count)
	return
}

func QueryStudentById(id int64) (item Student) {
	DbConnection.Where("id=?", id).First(&item)
	return
}

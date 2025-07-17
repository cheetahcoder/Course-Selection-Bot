DATABASE_TYPE = "mysql"

import json
import copy

if DATABASE_TYPE == "mysql":
    import mysql.connector
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="telegrambot"
    )



data = {}

def loadData():
    if DATABASE_TYPE == "json":
        dataFile = open ("./jsonDB/User_Data.json", "r", encoding="utf-8")
        data["usersData"] = json.load(dataFile)
        dataFile.close()

        dataFile = open ("./jsonDB/Admin.json", "r")
        data["admins"] = json.load(dataFile)
        dataFile.close()

        dataFile = open ("./jsonDB/Courses.json", "r", encoding="utf-8")
        data["courses"] = json.load(dataFile)
        dataFile.close()

        dataFile = open ("./jsonDB/Suggested_Courses.json", "r", encoding="utf-8")
        data["suggestCourse"] = json.load(dataFile)
        dataFile.close()

    elif DATABASE_TYPE == "mysql":
        data["usersData"] = []
        data["courses"] = {}
        data["suggestCourse"] = {}
        data["admins"] = []
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * FROM users_data")
        result = mycursor.fetchall()
        for i in result:
            data["usersData"].append({"ID" : i[1], "name" : i[2], "studentID" : i[3], "number" : i[4]})    
        
        mycursor.execute("SELECT * FROM admins")
        result = mycursor.fetchall()
        for i in result:
            data["admins"].append(i[1])    
        
        mycursor.execute("SELECT * FROM courses")
        result = mycursor.fetchall()
        for i in result:
            data["courses"][i[1]] = []

        mycursor.execute("SELECT * FROM course_values")
        result = mycursor.fetchall()
        for i in result:
            data["courses"][list(data["courses"].keys())[i[1]-1]].append(i[2])

        mycursor.execute("SELECT * FROM suggested_courses")
        result = mycursor.fetchall()
        for i in result:
            data["suggestCourse"][i[1]] = []
            if data["suggestCourse"].get(i[1]) is None:
                data["suggestCourse"][i[1]] = [i[2]]
            else:
                data["suggestCourse"][i[1]].append(i[2])

        
    return copy.deepcopy(data)

def saveLastData(usersData, courses, suggestCourse):
    if DATABASE_TYPE == "json":
        dataFile = open ("./jsonDB/User_Data.json", "w")
        dataFile.write(json.dumps(usersData))
        dataFile.close()

        dataFile = open ("./jsonDB/Courses.json", "w")
        dataFile.write(json.dumps(courses))
        dataFile.close()

        dataFile = open ("./jsonDB/Suggested_Courses.json", "w")
        dataFile.write(json.dumps(suggestCourse))
        dataFile.close()

    elif DATABASE_TYPE == "mysql":
        if not(usersData[-1] == data["usersData"][-1]):
            mycursor = mydb.cursor()
            sql = "INSERT INTO users_data (telegramID, name, studentID, number) VALUES (%s, %s, %s, %s)"
            val = tuple(usersData[-1].values())
            mycursor.execute(sql, val)
            mydb.commit()

            data["usersData"] = copy.deepcopy(usersData)
        
        if courses.keys() - data["courses"].keys():
            mycursor = mydb.cursor()
            sql = "INSERT INTO courses (name) VALUES (%s)"
            val = tuple(courses.keys() - data["courses"].keys())
            mycursor.execute(sql, val)
            mydb.commit()

            data["courses"] = copy.deepcopy(courses)

        if data["courses"].keys() - courses.keys():
            mycursor = mydb.cursor()
            sql = "DELETE FROM courses WHERE name = %s"
            adr = tuple(data["courses"].keys() - courses.keys())
            mycursor.execute(sql, adr)
            mydb.commit()

            data["courses"] = copy.deepcopy(courses)

        for i in data["courses"].keys():
            if set(courses[i]) - set(data["courses"][i]):
                mycursor = mydb.cursor()
                sql = "SELECT id FROM courses WHERE name = %s"
                adr = (i, )
                mycursor.execute(sql, adr)
                myresult = mycursor.fetchone()

                sql = "INSERT INTO course_values (courseID, telegramID) VALUES (%s, %s)"
                val = (myresult[0], tuple(set(courses[i]) - set(data["courses"][i]))[0])
                mycursor.execute(sql, val)
                mydb.commit()

                
            elif set(data["courses"][i]) - set(courses[i]):
                mycursor = mydb.cursor()
                sql = "SELECT id FROM courses WHERE name = %s"
                adr = (i, )
                mycursor.execute(sql, adr)
                myresult = mycursor.fetchone()

                sql = "DELETE FROM course_values WHERE courseID = %s AND telegramID = %s"
                adr = (myresult[0], tuple(set(data["courses"][i]) - set(courses[i]))[0])
                mycursor.execute(sql, adr)
                mydb.commit()
        data["courses"] = copy.deepcopy(courses)

        if suggestCourse.keys() - data["suggestCourse"].keys():
            mycursor = mydb.cursor()
            sql = "INSERT INTO suggested_courses (courseID, telegramID) VALUES (%s, %s)"
            val = (tuple(suggestCourse.keys() - data["suggestCourse"].keys())[0], suggestCourse[tuple(suggestCourse.keys() - data["suggestCourse"].keys())[0]][0])
            mycursor.execute(sql, val)
            mydb.commit()

        for i in data["suggestCourse"].keys():
            if set(suggestCourse[i]) - set(data["suggestCourse"][i]):
                mycursor = mydb.cursor()
                sql = "INSERT INTO suggested_courses (courseID, telegramID) VALUES (%s, %s)"
                val = (i, tuple(set(suggestCourse[i]) - set(data["suggestCourse"][i]))[0])
                mycursor.execute(sql, val)
                mydb.commit()
        data["suggestCourse"] = copy.deepcopy(suggestCourse)
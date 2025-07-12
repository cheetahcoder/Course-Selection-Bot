from telegram import Update, KeyboardButton,ReplyKeyboardRemove, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext
import json
import csv
import os
import matplotlib.pyplot as plt
from bidi.algorithm import get_display
import arabic_reshaper
import random


usersData = []
dataFile = open ("User_Data.json", "r", encoding="utf-8")
usersData = json.load(dataFile)
dataFile.close()

admins = []
dataFile = open ("Admin.json", "r")
admins = json.load(dataFile)
dataFile.close()

courses = {}
dataFile = open ("Courses.json", "r", encoding="utf-8")
courses = json.load(dataFile)
dataFile.close()

suggestCourse = {}
dataFile = open ("Suggested_Courses.json", "r", encoding="utf-8")
suggestCourse = json.load(dataFile)
dataFile.close()


def fixPersianText(text):
    reshapedText = arabic_reshaper.reshape(text)
    return get_display(reshapedText)

def makeColor(x):
    colors = []
    for i in range(x):
        color = (random.random(), random.random(), random.random())
        colors.append(color)
    return colors

def saveLastData():
    dataFile = open ("User_Data.json", "w")
    dataFile.write(json.dumps(usersData))
    dataFile.close()

    dataFile = open ("Courses.json", "w")
    dataFile.write(json.dumps(courses))
    dataFile.close()

    dataFile = open ("Suggested_Courses.json", "w")
    dataFile.write(json.dumps(suggestCourse))
    dataFile.close()

    


class Users():
    def checkUser(ID):
        for users in usersData:
            if users["ID"] == ID:
                return users
        return False
    
    def checkExistUser(studentID):
        for users in usersData:
            if users["studentID"] == studentID:
                return users
        return False
    
    def registerUser(ID, name, studentID, number):
        tempUser = {"ID" : ID, "name" : name, "studentID" : studentID, "number" : str(number)}
        usersData.append(tempUser)
        saveLastData()
        





async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    userID = update.message.from_user.id
    firstName = update.message.from_user.first_name

    ReplyKeyboardRemove()

    resultCheck = Users.checkUser(userID)
    if resultCheck:
        if userID in admins:
            buttons = [["📚 انتخاب واحد", "➕ درخواست درس جدید"], ["🔑 پنل مدیریت"]]
            reply = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            await update.message.reply_text("منوی دسترسی:", reply_markup=reply)
        else:
            buttons = ["📚 انتخاب واحد", "➕ درخواست درس جدید"]
            reply = ReplyKeyboardMarkup([buttons], resize_keyboard=True)
            await update.message.reply_text(f"👋 سلام {resultCheck['name']} عزیز!\n🎯 لطفا گزینه مورد نظر خود را از منوی زیر انتخاب کنید.", reply_markup=reply)
    else:
        await update.message.reply_text(f"👋 سلام {firstName} عزیز!\n🌟 برای ثبت‌نام، لطفا نام و نام خانوادگی خود را ارسال کنید:")
        context.user_data["level"] = 1

async def resiveMessage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userID = update.message.from_user.id
    firstName = update.message.from_user.first_name
    message = update.message.text
    if context.user_data.get("level"):
        if context.user_data["level"] == 1 :
            if message:
                context.user_data["name"] = message
                context.user_data["level"] = 2
                await update.message.reply_text("لطفاً کد دانشجویی خود را وارد کنید 📌")
            else:
                await update.message.reply_text("لطفاً نام خود را ارسال کنید 📌")
        elif context.user_data["level"] == 2 :
            if len(message) == 9 and message.isdigit():
                if not(Users.checkExistUser(message)):
                    context.user_data["studentId"] = message
                    context.user_data["level"] = 3
                    shareButton = KeyboardButton("Share Contact", request_contact=True)
                    reply = ReplyKeyboardMarkup([[shareButton]], resize_keyboard=True)
                    await update.message.reply_text("لطفاً شماره موبایل خود را وارد کنید 📱", reply_markup=reply)
                else:
                    await update.message.reply_text("⚠️ کد دانشجویی شما قبلاً ثبت شده است.\nدر صورت نیاز به کمک، با پشتیبانی تماس بگیرید.")
            else:
                await update.message.reply_text("🔢 کد دانشجویی باید 9 رقم باشد!\nلطفاً مجدداً آن را وارد کنید.") 
        elif context.user_data["level"] == 3 :
            contact = update.message.contact
            if contact:
                Users.registerUser(userID, context.user_data["name"], context.user_data["studentId"], contact.phone_number)
                
                buttons = ["📚 انتخاب واحد", "➕ درخواست درس جدید"]
                reply = ReplyKeyboardMarkup([buttons], resize_keyboard=True)
                await update.message.reply_text(f"سلام {context.user_data["name"]} عزیز! لطفا گزینه مورد نظر را انتخاب کنید.", reply_markup=reply) 
                context.user_data["level"] = 0
        
    else:
        if Users.checkUser(userID):
            if message == "📚 انتخاب واحد":
                message = "📚 دروس موجود برای انتخاب:\n\n"
                counter = 0
                keyboard = []
                for k,v in courses.items():
                    tempKeyboardMessage = ""
                    counter += 1
                    if userID in v:
                        message += ("✅ " + str(counter) + ". ")
                        tempKeyboardMessage += "✅ "
                    else:
                        message += ("❌ " + str(counter) + ". ")
                        tempKeyboardMessage += "❌ "
                    message += (k + "\n")
                    tempKeyboardMessage += k
                    keyboard.append([InlineKeyboardButton(tempKeyboardMessage, callback_data=k)])
                    
                        
           
                message += "\nبرای انتخاب یا حذف، روی دکمه‌های زیر کلیک کنید:"
                reply = InlineKeyboardMarkup(keyboard)

                await update.message.reply_text(message, reply_markup = reply)

            

            elif message == "↩️ بازگشت":

                if userID in admins:
                    if context.user_data.get("addcode"):
                        buttons = [["📚 انتخاب واحد", "➕ درخواست درس جدید"], ["🔑 پنل مدیریت"]]
                    else:
                        buttons = [["📈 گزارش انتخاب دروس", "🧑‍🎓 لیست کاربران"],["📖 لیست دروس", "❌ حذف درس", "➕ افزودن درس"], ["📝 گزارش درخواست دروس"], ["↩️ بازگشت به منوی کاربری"]]
                    reply = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
                    await update.message.reply_text("منوی دسترسی:", reply_markup=reply)
                else:
                    buttons = ["📚 انتخاب واحد", "➕ درخواست درس جدید"]
                    reply = ReplyKeyboardMarkup([buttons], resize_keyboard=True)
                    await update.message.reply_text("منوی دسترسی:", reply_markup=reply)

                context.user_data["addcode"] = False
                context.user_data["add"] = False
                context.user_data["remove"] = False
            
            elif message == "🔑 پنل مدیریت":

                if userID in admins:
                    buttons = [["📈 گزارش انتخاب دروس", "🧑‍🎓 لیست کاربران"],["📖 لیست دروس", "❌ حذف درس", "➕ افزودن درس"], ["📝 گزارش درخواست دروس"], ["↩️ بازگشت به منوی کاربری"]]
                    reply = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
                    await update.message.reply_text("منوی دسترسی:", reply_markup=reply)

            elif message == "↩️ بازگشت به منوی کاربری":

                if userID in admins:
                    buttons = [["📚 انتخاب واحد", "➕ درخواست درس جدید"], ["🔑 پنل مدیریت"]]
                    reply = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
                    await update.message.reply_text("منوی دسترسی:", reply_markup=reply)
                

            elif message == "➕ درخواست درس جدید":
                message = "لطفا کد درس درخواستی خود را وارد کنید:"
                context.user_data["addcode"] = True
                button =  [["↩️ بازگشت"]]
                reply = ReplyKeyboardMarkup(button, resize_keyboard=True)
                await update.message.reply_text(message, reply_markup=reply)

            elif context.user_data.get("addcode") == True:
                if len(message) == 5 and message.isdigit():

                    if userID in admins:
                        buttons = [["📚 انتخاب واحد", "➕ درخواست درس جدید"], ["🔑 پنل مدیریت"]]
                        reply = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
                    else:
                        buttons = ["📚 انتخاب واحد", "➕ درخواست درس جدید"]
                        reply = ReplyKeyboardMarkup([buttons], resize_keyboard=True)

                    if suggestCourse.get(message) is None:
                        suggestCourse[message] = [userID]
                    else:
                        if not(userID in suggestCourse[message]):
                            suggestCourse[message].append(userID)
                        else:
                            await update.message.reply_text("❌ شما قبلا برای این درس درخواست داده اید.", reply_markup=reply)
                            context.user_data["addcode"] = False
                            return

                    saveLastData()
                    context.user_data["addcode"] = False
                    await update.message.reply_text("✅ درخواست شما با موفقیت ثبت شد!", reply_markup=reply)
                else:
                    await update.message.reply_text("❌ کد وارد شده نادرست است.\nلطفا یک کد 5 رقمی معتبر وارد کنید:")
            
            
            if userID in admins:
                if message == "📈 گزارش انتخاب دروس":
                    message = "📊 گزارش انتخاب دروس:"
                    for k,v in courses.items():
                        message += ("\n\n🔹 درس: " + k)
                        message += ("\n   📋 تعداد انتخاب‌ها: " + str(len(v)))
                        message += "\n  🧑‍🎓 انتخاب‌شده توسط:\n"
                        for i in v:
                            message += ("     🔸 " + Users.checkUser(i)["name"] + " (کد: " + Users.checkUser(i)["studentID"] + ")\n")
                    buttons = [["📊 نمودار دروس", "📂 اکسل گزارش انتخاب دروس"], ["↩️ بازگشت"]]
                    reply = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
                    await update.message.reply_text(message, reply_markup=reply)                



                elif message == "📊 نمودار دروس":

                    for k,v in courses.items():
                        chartDatax = []
                        chartDatay = []

                        for i in v:
                            
                            if not(Users.checkUser(i)["studentID"][:4] in chartDatax):
                                chartDatax.append(Users.checkUser(i)["studentID"][:4])
                                chartDatay.append(1)
                            else:
                                indexData = chartDatax.index(Users.checkUser(i)["studentID"][:4])
                                chartDatay[indexData] += 1

                        colors = makeColor(len(chartDatax))
                        plt.bar(chartDatax, chartDatay, color=colors)
                        plt.title(fixPersianText(k))
                        plt.xlabel(fixPersianText("سال ورود"))
                        plt.ylabel(fixPersianText("تعداد دانشجو"))
                        plt.savefig(k + ".jpg")
                        plt.close()


                        f = open(k + ".jpg", "rb")
                        await update.message.reply_photo(photo=f)
                        f.close()

                        os.remove(k + ".jpg")

                elif message == "📂 اکسل گزارش انتخاب دروس":
                    dataFile = open("stats_report.csv", "w", encoding="utf-8-sig", newline="")
                    writer = csv.writer(dataFile)
                    writer.writerow(["Course Name", "Students Count"])

                    for k, v in courses.items():
                        writer.writerow([k, len(v)])

                    dataFile.close()

                    f = open("stats_report.csv", "rb")
                    await update.message.reply_document(document=f, filename="stats_report.csv")
                    f.close()

                
                    os.remove("stats_report.csv")


                    dataFile = open ("selection_report.csv", "w", encoding="utf-8-sig", newline="")
                    writer = csv.writer(dataFile)
                    writer.writerow(["Course Name", "Student Name", "Student ID"])
                    for course, users in courses.items():
                        if not users:
                            writer.writerow([course, "", ""])
                        else:
                            for i in users:
                                user = Users.checkUser(i)
                                writer.writerow([course, user["name"], user["studentID"]])

                    dataFile.close()

                    f = open("selection_report.csv", "rb")
                    await update.message.reply_document(document=f, filename="selection_report.csv")
                    f.close()

                    os.remove("selection_report.csv")
                
                elif message == "🧑‍🎓 لیست کاربران":
                    message = "🧑‍🎓 لیست کاربران:\n"
                    counter = 0
                    for i in usersData:
                        counter += 1
                        message += ("\n🔹 " + str(counter) + ". نام: " + i["name"] + " | " + " کد دانشجویی: " + i["studentID"] + " | " + " تلفن: " + i["number"])

                    await update.message.reply_text(message) 
                
                elif message == "📖 لیست دروس":
                    message = "📖 لیست دروس:\n"
                    counter = 0
                    for k,v in courses.items():
                        counter += 1
                        message += ("\n🔸 " + str(counter) + ". " + k)

                    await update.message.reply_text(message) 

                elif message == "➕ افزودن درس":
                    message = "لطفا نام درس را وارد کنید:"
                    context.user_data["add"] = True
                    button =  [["↩️ بازگشت"]]
                    reply = ReplyKeyboardMarkup(button, resize_keyboard=True)
                    await update.message.reply_text(message, reply_markup=reply)

                elif message == "❌ حذف درس":
                    message = "لطفا نام درس را وارد کنید:"
                    context.user_data["remove"] = True
                    button =  [["↩️ بازگشت"]]
                    reply = ReplyKeyboardMarkup(button, resize_keyboard=True)
                    await update.message.reply_text(message, reply_markup=reply)

                elif message == "📝 گزارش درخواست دروس":
                    message = "📝 گزارش درخواست دروس:"
                    for k,v in suggestCourse.items():
                        message += ("\n\n🔹 کد درس: " + k)
                        message += ("\n   📋 تعداد انتخاب‌ها: " + str(len(v)))
                    
                    await update.message.reply_text(message)   

                elif context.user_data.get("add") :
                    context.user_data["add"] = False
                    courses[message] = []
                    saveLastData()

                    buttons = [["📈 گزارش انتخاب دروس", "🧑‍🎓 لیست کاربران"],["📖 لیست دروس", "❌ حذف درس", "➕ افزودن درس"], ["📝 گزارش درخواست دروس"], ["↩️ بازگشت به منوی کاربری"]]
                    reply = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

                    await update.message.reply_text(f"درس '{message}' با موفقیت اضافه شد.",reply_markup=reply)

                elif context.user_data.get("remove") :
                    if message in courses:
                        context.user_data["remove"] = False
                        courses.pop(message)
                        saveLastData()

                        buttons = [["📈 گزارش انتخاب دروس", "🧑‍🎓 لیست کاربران"],["📖 لیست دروس", "❌ حذف درس", "➕ افزودن درس"], ["📝 گزارش درخواست دروس"], ["↩️ بازگشت به منوی کاربری"]]
                        reply = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

                        await update.message.reply_text(f"درس '{message}' با موفقیت حذف شد.",reply_markup=reply)
                    else:
                        await update.message.reply_text("❌ نام وارد شده نادرست است.\nلطفا یک نام درس معتبر وارد کنید:")



                

async def courseSelection(update: Update, context: CallbackContext):
    userID = update.callback_query.from_user.id
    courseName = update.callback_query.data
    if userID in courses[courseName]:
        courses[courseName].remove(userID)
    else:
        courses[courseName].append(userID)

    saveLastData()

    message = "📚 دروس موجود برای انتخاب:\n\n"
    counter = 0
    keyboard = []
    for k,v in courses.items():
        tempKeyboardMessage = ""
        counter += 1
        if userID in v:
            message += ("✅ " + str(counter) + ". ")
            tempKeyboardMessage += "✅ "
        else:
            message += ("❌ " + str(counter) + ". ")
            tempKeyboardMessage += "❌ "
        message += (k + "\n")
        tempKeyboardMessage += k
        keyboard.append([InlineKeyboardButton(tempKeyboardMessage, callback_data=k)])


    message += "\nبرای انتخاب یا حذف، روی دکمه‌های زیر کلیک کنید:"
    reply = InlineKeyboardMarkup(keyboard)

    await update.callback_query.answer(f"درس {courseName} تغییر کرد.") 
    await update.callback_query.message.edit_text(message, reply_markup = reply)
    



application = ApplicationBuilder().token("TOKEN").build()


application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, resiveMessage))
application.add_handler(MessageHandler(filters.CONTACT, resiveMessage))
application.add_handler(CallbackQueryHandler(courseSelection))


application.run_polling()
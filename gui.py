import time
from time import strftime
from datetime import date,datetime
import threading
import tkinter
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
import tkinter.font as tkFont
import serial
import os
import webbrowser





serial_data     = ''
raw_serial = None
filter_data = None
sat_stream1 = None
sat_stream2 = None
update_period = 2
serial_object = None
power = None
batt_percent = None
packages    = 0

#COLORS
color_gui_bg   = "#918D9E" 
color_frame_bg = "#918D9E"
color_terminal_bg   = "#11110F"
color_terminal_text = "#44F24F"
color_label_txt     = "#0D0D0D"

color_button_bg   = "#2F5956"
color_button_txt  = "#E7E8E9"
color_reportbtn_bg  = "#038C73"
color_mapsbtn_bg    = "#D94141"
color_entry_bg    = "#AB9FAB"

color_probar_tg = "#B3A7B3"
color_batt_bar  = "#18A367"
color_temp_bar  = "#FF6666"
color_rh_bar    = "#709BFF"
color_pess_bar  = "#1C8C7B"
color_salt_bar  = "#D9754C"
color_alt_bar   = "#D9BD57"


GUI = Tk()
GUI.title("CANSAT-Telemetry GUI")
GUI.configure(bg = color_gui_bg)  


#FONTS
font_frame_name = tkFont.Font(family="Alte Haas Grotesk" ,size=8,weight ="bold")
font_boldunder = tkFont.Font(family="Alte Haas Grotesk" ,size=9,weight ="bold",underline = 1)
font_data_1 = tkFont.Font(family="Alte Haas Grotesk" ,size=9)
font_terminal_txt = tkFont.Font(family="Envy Code R" ,size=11)
font_con_stat = tkFont.Font(family="Alte Haas Grotesk" ,size=11,weight ="bold")

#STYLES
ProgressBar_style = ttk.Style()
ProgressBar_style.configure("battery.Horizontal.TProgressbar", troughcolor=color_probar_tg, background = color_batt_bar)
ProgressBar_style.configure("temperature.Horizontal.TProgressbar", troughcolor=color_probar_tg, background=color_temp_bar)
ProgressBar_style.configure("rh.Horizontal.TProgressbar", troughcolor=color_probar_tg, background=color_rh_bar)
ProgressBar_style.configure("press.Horizontal.TProgressbar", troughcolor=color_probar_tg, background=color_pess_bar)
ProgressBar_style.configure("salt.Vertical.TProgressbar", troughcolor=color_probar_tg, background=color_salt_bar)
ProgressBar_style.configure("alt.Vertical.TProgressbar", troughcolor=color_probar_tg, background=color_alt_bar)

#VAR TEXT
conn_var    = StringVar()
disconn_var = StringVar()
disconn_var.set("DISCONNECTED")

def connect():
    """Esta funcion inicia la conexion al dispositivo UART
    El puerto y el Baudrate son definidos por el usuario
    Es posible elegir la plataforma para trabajar LINUX O WINDOWS"""

    global serial_object


    version_ = button_var.get()
    port = port_entry.get()
    baud = baud_entry.get()

    try:
        if version_ == 2:
            try:
                serial_object = serial.Serial('/dev/tty' + str(port), baudrate =baud, timeout = .05)
            
            except:
                print ("Cant Open Specified Port")
        elif version_ == 1:
            serial_object = serial.Serial( str(port), baudrate= baud, timeout = .05)
        elif version_ == 0:
            print ("seleccione SO")

    except ValueError:
        print ("Enter Baud and Port")
        return

    t1 = threading.Thread(target = get_data)
    t1.daemon = True
    t1.start()


def get_data():
    """Esta función sirve para recopilar datos del serial object y almacenar 
   los datos filtrados en dos vectores globales sat_strem1 & sat_stream2
   La función se ha colocado en un subproceso ya que el evento en serie es una función de bloqueo."""
    global serial_object
    global raw_serial
    global filter_data
    global sat_stream1
    global sat_stream2
    global update_period
    
    e = 0
    new = time.time()
    while e !=1:   
        try:
            serial_data = serial_object.readline().decode('utf-8')
            disconn_var.set("")
            conn_var.set("CONNECTED")
            
            
            if time.time() - new >= update_period:
                conn_var.set("")
                disconn_var.set("OFFLINE")
            
            if serial_data != "" :
                new = time.time()

                raw_serial = serial_data
                if raw_serial.startswith("#CAN"):
                    
                    data_flow.insert(END,"\n\r") 
                data_flow.insert(END,raw_serial)
                data_flow.see(END)
                

                filter_data = raw_serial.replace("\n","")
                if filter_data.startswith("#CAN"):
                    sat_stream1 = filter_data.replace("#CAN,","").split(",")
                    print(sat_stream1)
                
                    
                elif filter_data.startswith("\r#SAT"):
                    sat_stream2 = filter_data.replace("\r#SAT,","").split(",")
                    print(sat_stream2)
                                                                
            else:
                pass
        
            
        except TypeError:
            e=1
        except ValueError:
            print("ERROR")

        except AttributeError:
            conn_var.set("")
            disconn_var.set("DISCONNECTED")
            e=1
            messagebox.showinfo('Error','Unable to open serial port')
            
        except (OSError, serial.SerialException):
            conn_var.set("")
            disconn_var.set("DISCONNECTED")
            messagebox.showinfo('Port','Port Closed')
            e=1


def disconnect():
    conn_var.set("")
    disconn_var.set("DISCONNECTED")
    try:
        serial_object.close() 
  
    except AttributeError:
        messagebox.showinfo('Error','Port Closed')

        print ("Puerto cerado (Nunca se abrio)")

def send():
    #Funcion para enviar datos al microcontrolador
    send_data = send_data_entry.get()
    
    if not send_data:
        print ("Sent Nothing")
    
    serial_object.write(send_data.encode('utf-8'))

if __name__ == "__main__":
    
    ######FRAMES
    terminal_frame  = Frame(height = 145, width = 505, bd = 2, relief = 'groove',bg = color_gui_bg)
    terminal_frame.place(x = 7, y = 5)

    battery_frame   = Frame(height = 145, width = 270, bd = 2, relief = 'groove',bg = color_gui_bg)
    battery_frame.place(x = 515, y = 5)

    telemetry_frame = Frame(height = 245, width = 505, bd = 2, relief = 'groove',bg = color_gui_bg)
    telemetry_frame.place(x = 7, y = 155)

    telemetry1_frame = Frame(height = 105, width = 145, bd = 1, relief = 'groove',bg = color_frame_bg)
    telemetry1_frame.place(x = 20, y = 180)
    telemetry2_frame = Frame(height = 105, width = 145, bd = 1, relief = 'groove',bg = color_frame_bg)
    telemetry2_frame.place(x = 165, y = 180)
    telemetry3_frame = Frame(height = 105, width = 145, bd = 1, relief = 'groove',bg = color_frame_bg)
    telemetry3_frame.place(x = 20, y = 285)
    telemetry4_frame = Frame(height = 105, width = 145, bd = 1, relief = 'groove',bg = color_frame_bg)
    telemetry4_frame.place(x = 165, y = 285)
    
    telemetry2_frame = Frame(height = 210, width = 180, bd = 1, relief = 'groove',bg = color_frame_bg)
    telemetry2_frame.place(x = 320, y = 180)

    gps_frame_frame = Frame(height = 245, width = 270, bd = 2, relief = 'groove',bg = color_gui_bg)
    gps_frame_frame.place(x = 515, y = 155)

    conexion_frame  = Frame(height = 120, width = 505, bd = 2, relief = 'groove',bg = color_gui_bg)
    conexion_frame.place(x = 7, y = 405)

    ofiles_frame      = Frame(height = 120, width = 270, bd = 2, relief = 'groove',bg = color_gui_bg)
    ofiles_frame.place(x = 515, y = 405)

    status_frame    = Frame(height = 55, width = 778, bd = 2, relief = 'groove',bg = color_gui_bg)
    status_frame.place(x = 7, y = 530)

    ######TERMINAL
    data_flow = Text(width = 59, height = 6,bg=color_terminal_bg,fg =color_terminal_text,font = font_terminal_txt)
    data_flow.place(x = 20, y = 26)

    ######FRAME LABELS
    Label(text = "Terminal",bg = color_gui_bg,fg = color_label_txt,font = font_frame_name).place(x = 20, y =8)
    Label(text = "Battery Status",bg = color_gui_bg,fg = color_label_txt,font = font_frame_name).place(x = 530, y =8)
    Label(text = "Telemetry",bg = color_gui_bg,fg = color_label_txt,font = font_frame_name).place(x = 20, y =160)
    Label(text = "GPS Data",bg = color_gui_bg,fg = color_label_txt,font = font_frame_name).place(x = 530, y =158)
    Label(text = "Session",bg = color_gui_bg,fg = color_label_txt,font = font_frame_name).place(x = 20, y =408)
    Label(text = "Statistics",bg = color_gui_bg,fg = color_label_txt,font = font_frame_name).place(x = 530, y =408)
    Label(text = "Status",bg = color_gui_bg,fg = color_label_txt,font = font_frame_name).place(x = 20, y =533)

    ######STATICS LABELS
    #BATTERY LAB
    Label(text = "Voltage:",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 530, y =40)
    Label(text = "Current:",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 640, y =40)
    Label(text = "Power:",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 530, y =70)
    Label(text = "Remaining Percent:",bg = color_gui_bg,fg = color_label_txt,font = ("Alte Haas Grotesk" ,8)).place(x = 570, y =100)
    #TELEMETRY LAB
    Label(text = "DH22 | Temperature",font = font_data_1,bg = color_frame_bg,fg = color_label_txt).place(x = 92, y= 195,anchor= "center")
    Label(text = "BME | Temperature",font = font_data_1,bg = color_frame_bg,fg = color_label_txt).place(x = 237, y= 195,anchor= "center")
    Label(text = "R. Humidity",font = font_data_1,bg = color_frame_bg,fg = color_label_txt).place(x = 92, y= 300,anchor= "center")
    Label(text = "Pressure:",font = font_data_1,bg = color_frame_bg,fg = color_label_txt).place(x = 237, y= 300,anchor= "center")
    Label(text = "A. Altitude:",font = font_data_1,bg = color_frame_bg,fg = color_label_txt).place(x = 370, y= 350,anchor= "center")
    Label(text = "Altitude:",font = font_data_1,bg = color_frame_bg,fg = color_label_txt).place(x = 450, y= 350,anchor= "center")
    #GPS DATA LAB
    Label(text = "Date/Time",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 650, y =180, anchor= "center")
    Label(text = "Satellites",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 650, y =230, anchor= "center")
    Label(text = "Geographical Coordinates",bg = color_gui_bg,fg = color_label_txt,font = font_boldunder).place(x = 650, y =280, anchor= "center")
    Label(text = "Latitude :",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 570, y =300)
    Label(text = "Longitude:",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 570, y =320)
    #CONECTION LAB
    Label(text = "Baud:",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 90, y = 466)
    Label(text = "Port:",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 20, y = 466)
    #STATUS LAB
    Label(textvariable = disconn_var,bg = color_gui_bg,fg = "#F20F0F",font = font_con_stat).place(x = 21, y =555)
    Label(textvariable = conn_var,bg = color_gui_bg,fg = "#13F235",font = font_con_stat).place(x = 20, y =555)
    
    ######ENTRY
    send_data_entry = Entry(width = 7,bg = color_entry_bg, fg = color_terminal_bg)
    send_data_entry.place(x = 360, y = 485)
    
    baud_entry = Entry(width = 6, bg = color_entry_bg, fg = color_terminal_bg,font = font_data_1)
    baud_entry.insert(INSERT,"57600")
    baud_entry.place(x = 90, y = 485)
    
    port_entry = Entry(width = 6, bg = color_entry_bg, fg = color_terminal_bg,font = font_data_1)
    port_entry.insert(INSERT,"USB0")
    port_entry.place(x = 20, y = 485)

    ######RADIO BUTTONS
    button_var = IntVar()
    Radiobutton(text = "Windows",width=8, variable = button_var, value = 1,bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 20, y = 435)
    Radiobutton(text = "Linux",width=7, variable = button_var, value = 2,bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 120, y = 435)

    ######BUTTONS
    Button(text = "Send",font = ("Alte Haas Grotesk",8), command = send, width = 6,bg=color_button_bg,fg = color_button_txt).place(x = 430, y = 483)
    Button(text = "Connect",font = ("Alte Haas Grotesk",8),command = connect,width= 9,bg=color_button_bg,fg = color_button_txt).place(x = 150, y = 483)
    Button(text = "Disconnect",font = ("Alte Haas Grotesk",8), command = disconnect,width= 9,bg=color_button_bg,fg = color_button_txt).place(x =250, y = 483)
    

    ######PROGRESS BAR
    battery_bar = ttk.Progressbar(style="battery.Horizontal.TProgressbar",orient = HORIZONTAL, mode = 'determinate', length = 240, max = 100)
    battery_bar.place(x = 530, y = 120)

    temperature_bar1 = ttk.Progressbar(style="temperature.Horizontal.TProgressbar",orient = HORIZONTAL, mode = 'determinate', length = 125, max = 80)
    temperature_bar1.place(x = 92, y = 260,anchor = "center")
    
    temperature_bar2 = ttk.Progressbar(style="temperature.Horizontal.TProgressbar",orient = HORIZONTAL, mode = 'determinate', length = 125, max = 80)
    temperature_bar2.place(x = 237, y = 260,anchor = "center")
    
    humidity_bar = ttk.Progressbar(style="rh.Horizontal.TProgressbar",orient = HORIZONTAL, mode = 'determinate', length = 125, max = 100)
    humidity_bar.place(x = 92, y = 365,anchor = "center")
    
    pressure_bar = ttk.Progressbar(style="press.Horizontal.TProgressbar",orient = HORIZONTAL, mode = 'determinate', length = 125, max = 2000)
    pressure_bar.place(x = 237, y = 365,anchor = "center")
    
    salt_bar = ttk.Progressbar(style="salt.Vertical.TProgressbar",orient = VERTICAL, mode = 'determinate', length = 150, max = 5000)
    salt_bar.place(x = 370, y = 265,anchor ="center")
    
    alt_bar = ttk.Progressbar(style="alt.Vertical.TProgressbar",orient = VERTICAL, mode = 'determinate', length = 150, max = 100)
    alt_bar.place(x = 450, y = 265,anchor ="center")


    #mainloop
    GUI.geometry('800x600')
    GUI.mainloop()

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
import math  
import csv

current_directory = os.getcwd()
ofiles_directory = os.path.join(current_directory, r'output_files')
if not os.path.exists(ofiles_directory):
    os.makedirs(ofiles_directory)
session_directory = ""

writer = None
telemetry_values= ["Time","DHT Temp","BME Temp","R.H","Pressure","Altitude","Voltage","Current"]
gps_values = ["Time","Latitude","Longitude","Satellites"]

b = 0.0000225577
k = 5.2559
q=0
serial_data     = ''
raw_serial = None
filter_data = None
sat_stream1 = None
sat_stream2 = None
update_period = 2
serial_object = None
power = None
batt_percent = None
packets    = 0
packets_errors    = 0
sea_altitude = 0.0
altitude = 0.0
gps_coors = 0

gps_start = None
gps_end   = None

#LINK
LINK_LAT = None
LINK_LONG = None

#CONSTANTS
BATTERY_MIN = 2.9
BATTERY_MAX = 4.1



#COLORS
color_gui_bg   = "#918D9E" 
color_frame_bg = "#262A33"
color_terminal_bg   = "#262A33"
color_terminal_text = "#44F24F"
color_label_txt     = "#0D0D0D"

color_button_bg   = "#56545E"
color_button_txt  = "#E7E8E9"
color_reportbtn_bg  = "#038C73"
color_mapsbtn_bg    = "#D94141"
color_entry_bg    = "#9C98AB"

color_border = "#797685"
color_probar_tg = "#9C98AB"
color_border2 = "#56545E"
color_batt_bar  = "#18A367"
color_temp_bar  = "#D0363E"
color_rh_bar    = "#4999AB"
color_pess_bar  = "#3F8C54"
color_salt_bar  = "#2E606B"
color_alt_bar   = "#59433A"


GUI = Tk()
GUI.title("CANSAT-Telemetry GUI")
GUI.configure(bg = color_gui_bg)  


#FONTS
font_frame_name = tkFont.Font(family="Alte Haas Grotesk" ,size=8,weight ="bold")
font_boldunder = tkFont.Font(family="Alte Haas Grotesk" ,size=9,weight ="bold",underline = 1)
font_data_1 = tkFont.Font(family="Alte Haas Grotesk" ,size=10)
font_terminal_txt = tkFont.Font(family="Envy Code R" ,size=11)
font_con_stat = tkFont.Font(family="Alte Haas Grotesk" ,size=11,weight ="bold")
font_con_stat1 = tkFont.Font(family="Alte Haas Grotesk" ,size=13,weight ="bold")
font_var_bold = tkFont.Font(family="Alte Haas Grotesk" ,size=11,weight ="bold")

#STYLES
ProgressBar_style = ttk.Style()
ProgressBar_style.theme_use('clam')
ProgressBar_style.configure("battery.Horizontal.TProgressbar", troughcolor=color_probar_tg, background = color_batt_bar,bordercolor=color_border, lightcolor=color_border2, darkcolor=color_border2)
ProgressBar_style.configure("temperature.Horizontal.TProgressbar", troughcolor=color_probar_tg, background=color_temp_bar,bordercolor=color_border, lightcolor=color_border2, darkcolor=color_border2)
ProgressBar_style.configure("rh.Horizontal.TProgressbar", troughcolor=color_probar_tg, background=color_rh_bar,bordercolor=color_border, lightcolor=color_border2, darkcolor=color_border2)
ProgressBar_style.configure("press.Horizontal.TProgressbar", troughcolor=color_probar_tg, background=color_pess_bar,bordercolor=color_border, lightcolor=color_border2, darkcolor=color_border2)
ProgressBar_style.configure("salt.Vertical.TProgressbar", troughcolor=color_probar_tg, background=color_salt_bar,bordercolor=color_border, lightcolor=color_border2, darkcolor=color_border2)
ProgressBar_style.configure("alt.Vertical.TProgressbar", troughcolor=color_probar_tg, background=color_alt_bar,bordercolor=color_border, lightcolor=color_border2, darkcolor=color_border2)

#VAR TEXT
conn_var    = StringVar()
disconn_var = StringVar()
disconn_var.set("DISCONNECTED")

GPS_DataTime = StringVar()
GPS_Satellites = StringVar()
GPS_Lat = StringVar()
GPS_Lon = StringVar()

Tel_Temp1   = StringVar()
Tel_Temp2   = StringVar()
Tel_RH      = StringVar()
Tel_Press   = StringVar()
Tel_SAlt    = StringVar()
Tel_Alt     = StringVar()


Batt_Volt   = StringVar()
Batt_Curr   = StringVar()
Batt_Power  = StringVar()
Batt_Perc   = StringVar()

data_r   = StringVar()
data_err   = StringVar()

tv_uptime = StringVar()
tv_uptime.set("00 : 00 : 00")

def cron():
    global q
    
    for h in range (0,24):
        if (q==1 ):
            break
        for m in range(0,60):
            if (q==1 ):
                break
            for s in range (0,60):
                if (q==1 ):
                    break
                tv_uptime.set("{:02d} : {:02d} : {:02d}".format(h,m,s)) 
                time.sleep(1)



def connect():
    """Esta funcion inicia la conexion al dispositivo UART
    El puerto y el Baudrate son definidos por el usuario
    Es posible elegir la plataforma para trabajar LINUX O WINDOWS"""

    global serial_object
    global t_up
    global session_directory
    global writer
    global q
    global gps_coors
    global packets
    version_ = button_var.get()
    port = port_entry.get()
    baud = baud_entry.get()

    try:
        if version_ == 2:
            try:
                serial_object = serial.Serial('/dev/tty' + str(port), baudrate =baud, timeout = 1)
                session_directory = ofiles_directory + strftime("/%Y-%m-%d_%H%M%S")
                os.makedirs(session_directory)
            
            except:
                
                q = 1
                gps_coors = 0
                packets = 0
                print ("Cant Open Specified Port")
                
        elif version_ == 1:
            serial_object = serial.Serial( str(port), baudrate= baud, timeout = 1)
            session_directory = ofiles_directory + strftime("/%Y-%m-%d_%H%M%S")
            os.makedirs(session_directory)

            with open(session_directory + "/Telemetry.csv",'w',newline='') as file:
                writer = csv.writer(file,delimiter = ',')
                writer.writerow(telemetry_values)

            with open(session_directory + "/GPS.csv",'w',newline='') as file:
                writer = csv.writer(file,delimiter = ',')
                writer.writerow(gps_values)    
        elif version_ == 0:
            print ("seleccione SO")

    except ValueError:
        print ("Enter Baud and Port")
        return
    q=0
    t1 = threading.Thread(target = get_data)
    t1.daemon = True
    t1.start()
    t_up = threading.Thread(target= cron)
    #t_up.daemon = True
    t_up.start()

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
    global packets
    global writer
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
                
                filter_data = raw_serial.replace("\n","").replace("\r","").replace("\n\r","")
               
                
                if filter_data.startswith("#CAN"):
                    sat_stream1 = filter_data.replace("#CAN,","").split(",")
                    print(sat_stream1)
                           
                if filter_data.startswith("#SAT"):
                    sat_stream2 = filter_data.replace("#SAT,","").split(",")
                    print(sat_stream2)
                
                
                                                        
            else:
                pass
        
            
        except TypeError:
            e=1
        except ValueError:
            print("ERROR EN EL PUERTO")

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

        

def update_gui():

    global sat_stream1
    global sat_stream2
    global LINK_LAT
    global LINK_LONG
    global packets
    global packets_errors
    global writer
    global gps_coors
    global gps_start
    while(1):

        if sat_stream1 != None:
            try:
                if(len(sat_stream1) == 6):
                    packets = packets + 1
                else:
                    packets_errors = packets_errors + 1
            except:
                pass
            try:
                if(sat_stream1[0] != ""):
                    GPS_DataTime.set(strftime("%d/%m/%y")+"  |  "+sat_stream1[0]+":"+sat_stream1[1]+":"+sat_stream1[2])
                    
                    LAT = sat_stream1[3].replace("S","-").replace("N","")
                    LAT = float(LAT)/100
                    LAT = round(int(LAT) + ((LAT-int(LAT))*(5/3)),7)

                    LONG = sat_stream1[4].replace("W","-").replace("E","")
                    LONG = float(LONG)/100
                    LONG = round(int(LONG) + ((LONG-int(LONG))*(5/3)),7)

                    GPS_Lat.set(LAT)
                    GPS_Lon.set(LONG)
                    LINK_LAT = str(LAT)
                    LINK_LONG = str(LONG)
                    GPS_Satellites.set(sat_stream1[5])
                    
                try:
                    if(sat_stream1[3] != ""):
                        gps_coors = gps_coors + 1
                        if(gps_coors == 1):
                            make_earth_file()
                            gps_start = strftime("%y/%m/%d at %H:%M:%S")
                        if (gps_coors >= 1):
                            efile = open(session_directory + '/Trajectory.kml','a')
                            efile.write(LINK_LONG+","+LINK_LAT+"\n")
                            efile.close()
                        gps_data = [strftime("%H:%M:%S"),LAT,LONG,sat_stream1[5]]
                        with open(session_directory + "/GPS.csv",'a',newline='') as file:
                            writer = csv.writer(file,delimiter = ',')
                            writer.writerow(gps_data)
                except:
                    pass    
            except:
                print("stream1 Err")
            sat_stream1 = None
            
        if sat_stream2 != None:
            try:
                if(len(sat_stream2) == 7):
                    packets = packets + 1
                else:
                    packets_errors = packets_errors + 1
            except:
                pass
            try:
                Tel_Temp1.set(sat_stream2[0])
                Tel_RH.set(sat_stream2[1])
                Tel_Temp2.set(sat_stream2[2])
                Tel_Press.set(sat_stream2[3])        
                Batt_Volt.set(sat_stream2[5] + " V")
                Batt_Curr.set(sat_stream2[6] + " mA")
            except:
                print("stream2 Err")  
            try:
                power = ((float(sat_stream2[5])*1000)* float(sat_stream2[6]))/1000
                Batt_Power.set(str(round(power,2)) + " mW")

                batt_percent = ((float(sat_stream2[5]) - BATTERY_MIN)*100)/(BATTERY_MAX-BATTERY_MIN)
                Batt_Perc.set(str(round(batt_percent)) + " %")

                sea_altitude = round(((1-((float(sat_stream2[3])) / 1013.25)**(1/k)) / b),2)
                Tel_SAlt.set(str(sea_altitude) + " m")

                altitude = round(float(sat_stream2[3]) + float(sat_stream2[4]),2)
                altitude = round(sea_altitude - (round(((1-((altitude) / 1013.25)**(1/k)) / b),2)),2)
                Tel_Alt.set(str(altitude) + " m")

            except:
                print("Math Err")
            try:
                temperature_bar1["value"] = sat_stream2[0]
                humidity_bar["value"] = sat_stream2[1]
                temperature_bar2["value"] = sat_stream2[2]
                pressure_bar["value"] = sat_stream2[3]
                battery_bar["value"] = batt_percent
                salt_bar["value"] = sea_altitude
                alt_bar["value"] = altitude
            except:
                print("PBars Err")
            try:
                data_r.set(packets)
                data_err.set(packets_errors)
                Telemetry_data = [strftime("%H:%M:%S"),sat_stream2[0],sat_stream2[2],sat_stream2[1],sat_stream2[3],sea_altitude,sat_stream2[5],sat_stream2[6]]
                with open(session_directory + "/Telemetry.csv",'a',newline='') as file:
                    writer = csv.writer(file,delimiter = ',')
                    writer.writerow(Telemetry_data)
            except:
                pass
            sat_stream2 = None   
            
        time.sleep(.1)

def make_earth_file():
    """make a google earth file"""
    global session_directory

    efile = open(session_directory + '/Trajectory.kml','w')
    efile.write(
      
"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"> <Document>
<name>Trajectory</name>
<description>CANSAT Trajectory</description> <Style id="yellowLineGreenPoly">
<LineStyle>
<color>7f00ffff</color>
<width>4</width>
</LineStyle>
<PolyStyle>
<color>7f00ff00</color>
</PolyStyle>
</Style> <Placemark>
<styleUrl>#yellowLineGreenPoly</styleUrl>
<LineString>
<extrude>1</extrude>
<tessellate>1</tessellate>
<altitudeMode>absoluto</altitudeMode>

<coordinates>


""")
    efile.close()

def close_earth_file():
    global session_directory
    global gps_start
    efile = open(session_directory + '/Trajectory.kml','a')
    efile.write("""
</coordinates>
</LineString> 
<name>CANSAT Trajectory</name>
<description>\n""")
    efile.write("<b>Start: </b>"+gps_start+"<br/>\n")
    efile.write("<b>End:</b> "+strftime("%y/%m/%d at %H:%M:%S")+"\n")
    efile.write("""

</description>
</Placemark>
 </Document> </kml>  
    """)
    efile.close()

def disconnect():
    global q
    global gps_coors
    global packets
    q = 1
    gps_coors = 0
    packets = 0
    close_earth_file()
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

def gmaps():
    webbrowser.open("https://www.google.com/maps/search/?api=1&query="+ LINK_LAT + "," + LINK_LONG)

if __name__ == "__main__":
    
    ######FRAMES
    terminal_frame  = Frame(height = 145, width = 505, bd = 2, relief = 'groove',bg = color_gui_bg)
    terminal_frame.place(x = 7, y = 5)

    battery_frame   = Frame(height = 145, width = 270, bd = 2, relief = 'groove',bg = color_gui_bg)
    battery_frame.place(x = 515, y = 5)

    telemetry_frame = Frame(height = 245, width = 505, bd = 2, relief = 'groove',bg = color_gui_bg)
    telemetry_frame.place(x = 7, y = 155)

    telemetry1_frame = Frame(height = 105, width = 145, bd = 1, relief = 'groove',bg = color_gui_bg)
    telemetry1_frame.place(x = 20, y = 180)
    telemetry2_frame = Frame(height = 105, width = 145, bd = 1, relief = 'groove',bg = color_gui_bg)
    telemetry2_frame.place(x = 165, y = 180)
    telemetry3_frame = Frame(height = 105, width = 145, bd = 1, relief = 'groove',bg = color_gui_bg)
    telemetry3_frame.place(x = 20, y = 285)
    telemetry4_frame = Frame(height = 105, width = 145, bd = 1, relief = 'groove',bg = color_gui_bg)
    telemetry4_frame.place(x = 165, y = 285)
    
    telemetry2_frame = Frame(height = 210, width = 180, bd = 1, relief = 'groove',bg = color_gui_bg)
    telemetry2_frame.place(x = 320, y = 180)

    gps_frame_frame = Frame(height = 245, width = 270, bd = 2, relief = 'groove',bg = color_gui_bg)
    gps_frame_frame.place(x = 515, y = 155)

    conexion_frame  = Frame(height = 120, width = 505, bd = 2, relief = 'groove',bg = color_gui_bg)
    conexion_frame.place(x = 7, y = 405)

    ofiles_frame      = Frame(height = 120, width = 270, bd = 2, relief = 'groove',bg = color_gui_bg)
    ofiles_frame.place(x = 515, y = 405)

    status_frame    = Frame(height = 65, width = 778, bd = 2, relief = 'groove',bg = color_gui_bg)
    status_frame.place(x = 7, y = 530)

    con_frame    = Frame(height = 32, width = 140, bd = 0, relief = 'groove',bg = color_frame_bg)
    con_frame.place(x = 16, y = 553)

    #logo = PhotoImage(file = "logo.png")
    #log = Label(GUI,image = logo).place(x=560,y=533)
    ######TERMINAL
    data_flow = Text(width = 59, height = 6,bg=color_terminal_bg,fg =color_terminal_text,font = font_terminal_txt)
    data_flow.place(x = 20, y = 28)

    t2 = threading.Thread(target = update_gui)
    t2.daemon = True
    t2.start()

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
    Label(text = "DH22 | Temperature",font = font_data_1,bg = color_gui_bg,fg = color_label_txt).place(x = 92, y= 195,anchor= "center")
    Label(text = "°C" ,font = ("DS-Digital",15),bg = color_gui_bg,fg = color_label_txt).place(x = 135, y= 225,anchor= "center")
    Label(text = "BME | Temperature",font = font_data_1,bg = color_gui_bg,fg = color_label_txt).place(x = 237, y= 195,anchor= "center")
    Label(text = "°C" ,font = ("DS-Digital",15),bg = color_gui_bg,fg = color_label_txt).place(x = 280, y= 225,anchor= "center")
    Label(text = "R. Humidity",font = font_data_1,bg = color_gui_bg,fg = color_label_txt).place(x = 92, y= 300,anchor= "center")
    Label(text = "%" ,font = ("DS-Digital",18),bg = color_gui_bg,fg = color_label_txt).place(x = 135, y= 330,anchor= "center")
    Label(text = "Pressure:",font = font_data_1,bg = color_gui_bg,fg = color_label_txt).place(x = 237, y= 300,anchor= "center")
    Label(text = "hp" ,font = ("DJB Get Digital" ,13),bg = color_gui_bg,fg = color_label_txt).place(x = 290, y= 330,anchor= "center")
    Label(text = "A. Altitude:",font = font_data_1,bg = color_gui_bg,fg = color_label_txt).place(x = 370, y= 350,anchor= "center")
    Label(text = "Altitude:",font = font_data_1,bg = color_gui_bg,fg = color_label_txt).place(x = 450, y= 350,anchor= "center")
    #GPS DATA LAB
    Label(text = "Date/Time",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 650, y =180, anchor= "center")
    Label(text = "Satellites",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 650, y =230, anchor= "center")
    Label(text = "Geographical Coordinates",bg = color_gui_bg,fg = color_label_txt,font = font_boldunder).place(x = 650, y =280, anchor= "center")
    Label(text = "Latitude :",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 570, y =300)
    Label(text = "Longitude:",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 570, y =320)
    #CONECTION LAB
    Label(text = "Baud:",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 90, y = 466)
    Label(text = "Port:",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 20, y = 466)
    #STATISTICS LAB
    Label(text = "Packets:",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 530, y =438)
    Label(text = "Errors:",bg = color_gui_bg,fg = color_label_txt,font = font_data_1).place(x = 670, y =438)
    #STATUS LAB
    Label(textvariable = disconn_var,bg = color_frame_bg,fg = color_temp_bar,font = font_con_stat).place(x = 22, y =558)
    Label(textvariable = conn_var,bg = color_frame_bg,fg = color_terminal_text,font = font_con_stat1).place(x = 20, y =557)
    Label(text = "Uptime: ",bg = color_gui_bg,fg = color_frame_bg,font = font_con_stat1).place(x = 200, y =555)

    ######VARIABLE LABEL
    #BATTERY
    Label(textvariable = Batt_Volt,font = font_var_bold,bg = color_gui_bg,fg = color_label_txt).place(x = 585, y= 40)
    Label(textvariable = Batt_Curr,font = font_var_bold,bg = color_gui_bg,fg = color_label_txt).place(x = 695, y= 40)
    Label(textvariable = Batt_Power,font = font_var_bold,bg = color_gui_bg,fg = color_label_txt).place(x = 580, y= 70)
    Label(textvariable = Batt_Perc,font = font_var_bold,bg = color_gui_bg,fg = color_label_txt).place(x = 675, y= 95)
    #TELEMETRY 
    Label(textvariable = Tel_Temp1,font = "DS-Digital 24 bold",bg = color_gui_bg,fg = color_label_txt).place(x = 60, y= 210)
    Label(textvariable = Tel_Temp2,font = "DS-Digital 24 bold",bg = color_gui_bg,fg = color_label_txt).place(x = 190, y= 210)
    Label(textvariable = Tel_RH,font = "DS-Digital 24 bold",bg = color_gui_bg,fg = color_label_txt).place(x = 92, y= 330,anchor= "center")
    Label(textvariable = Tel_Press,font = "DS-Digital 20 bold",bg = color_gui_bg,fg = color_label_txt).place(x = 237, y= 330,anchor= "center")
    Label(textvariable = Tel_SAlt,font = ("DJB Get Digital",15),bg = color_gui_bg,fg = color_label_txt).place(x = 370, y= 370,anchor= "center")
    Label(textvariable = Tel_Alt,font = ("DJB Get Digital",15),bg = color_gui_bg,fg = color_label_txt).place(x = 450, y= 370,anchor= "center")
    #GPS DATA
    Label(textvariable = GPS_DataTime,bg = color_gui_bg,fg = color_label_txt,font = font_var_bold).place(x = 650, y =200, anchor= "center")
    Label(textvariable = GPS_Satellites,bg = color_gui_bg,fg = color_label_txt,font = font_var_bold).place(x = 650, y =250, anchor= "center")
    Label(textvariable = GPS_Lat,bg = color_gui_bg,fg = color_label_txt,font = font_var_bold).place(x = 650, y =300)
    Label(textvariable = GPS_Lon,bg = color_gui_bg,fg = color_label_txt,font = font_var_bold).place(x = 645, y =320)
    #STATISTICS 
    Label(textvariable = data_r,font = font_var_bold,bg = color_gui_bg,fg = color_label_txt).place(x = 590, y= 438)
    Label(textvariable = data_err,font = font_var_bold,bg = color_gui_bg,fg = color_label_txt).place(x = 720, y= 438)
    #SATATUS
    Label(textvariable = tv_uptime,bg = color_gui_bg,fg = color_frame_bg,font = ("DJB Get Digital",20)).place(x = 280, y =550)

    ######ENTRY
    send_data_entry = Entry(width = 8,bg = color_entry_bg, fg = color_terminal_bg)
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
    Button(text = "Send",font = ("Alte Haas Grotesk",8), command = send, width = 10,bg=color_button_bg,fg = color_button_txt).place(x = 430, y = 483)
    Button(text = "Connect",font = ("Alte Haas Grotesk",8),command = connect,width= 12,bg=color_button_bg,fg = color_button_txt).place(x = 150, y = 483)
    Button(text = "Disconnect",font = ("Alte Haas Grotesk",8), command = disconnect,width= 12,bg=color_button_bg,fg = color_button_txt).place(x =250, y = 483)
    Button(text = "Google Maps", command = gmaps, width =15 ,bg=color_mapsbtn_bg,fg = color_button_txt,font = ("Alte Haas Grotesk",12)).place(x = 650, y = 370,anchor = "center")


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
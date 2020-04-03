#!/usr/bin/python

############################
#--AUTORES DE LA PRACTICA--#
#--------------------------#
#----Hugo Pascual Adan-----#
#-------Jakub Piatek-------#
############################

#PARA VER LAS POSIBLES ORDENES EJECUTAR EL SCRIPT SIN ARGUMENTOS

############################
#---MEJORAS INTRODUCIDAS---#
############################

#MEJORA 1: control del entorno con variables boolenas de forma que no se pueda arrancar sin haber creado,
#ni parar sin haber arrancado, ni destruir sin haber creado, etc. El estado del entorno se guarda en el
#fichero de configuracion pf1.cfg y se lee y modifica a traves de las funciones getVarBool y setVarBool.

#MEJORA 2: monitorizacion del escenario. Se permite hacer ping a cualquiera de las maquinas (ping), 
#listar las las maquinas (list), visualizar las estadisticas de CPU de cada maquina (watch) y ver las
#estadisticas del balanceador de carga implementado en el lb (balance-stats). 

#MEJORA 3: implementacion del balanceador de trafico HAproxy en la maquina lb. Ademas, ejecutando la
#orden "monitor balance-stats" de la MEJORA 2 se puede acceder a la pagina para visualizar las
#estadisticas.

#MEJORA 4: funcionalidad de arrancar y parar maquinas individualmente por medio de las ordenes run_one
#y stop_one, respectivamente.


from subprocess import call
import sys
import os
import shutil
import subprocess


#####################################################################
#-----------------------------FUNCIONES-----------------------------#
#####################################################################

#borrar: borra la carpeta y todos los archivos que contiene dentro
def borrar(folder):
	for the_file in os.listdir(folder): 
		file_path = os.path.join(folder, the_file)
		try: 
			if os.path.isfile(file_path): 
				os.remove(file_path)
				print("Archivo " + the_file +" borrado") 
		except Exception, e: 
			print e
	try:
		os.rmdir(folder)
	except OSError as os.errno.ENOTEMPTY:
		print "Directory not empty"
	print("Se ha borrado la carpeta "+str(folder))

##borrarSilencioso: borra la carpeta con todos los archivos que contiene
def borrarSilencioso(folder):
	for the_file in os.listdir(folder): 
		file_path = os.path.join(folder, the_file)
		try: 
			if os.path.isfile(file_path): 
				os.remove(file_path)
		except Exception, e: 
			print e
	try:
		os.rmdir(folder)
	except OSError as os.errno.ENOTEMPTY:
		print "Directory not empty"

#getNServ:lee el numero de servidores del archivo de configuracion
def getNServ():
	fin = open(ruta_cfg, "r");
	for line in fin:
		if "num_serv=" in line:
			valor=int(line[9]);#porque el valor esta en la posicion 9 empezando por el 0
	fin.close();
	return valor;

#getVarBool: lee del fichero de configuracion el estado del entorno (funcion utilizada para la MEJORA 1)
def getVarBool(var):
	try:
		fin = open(ruta_cfg, "r");
		for line in fin:
			if var in line:
				longitud=len(var)
				valor=int(line[longitud+1])
				break;
		fin.close();
		return bool(valor);			
	except:
		return False;

#setVarBool: escribe en el fichero de configuracion el estado del entorno
def setVarBool(var,estado):
	ruta_cfg_aux=ruta_dir+"aux.cfg";
	call(["cp", ruta_cfg, ruta_cfg_aux])
	fin=open(ruta_cfg_aux,"r");
	fout=open(ruta_cfg,"w");
	for line in fin:
		if var in line:
			fout.write(var+"="+str(estado)+"\n");
		else:
			fout.write(line);
	fin.close();
	fout.close();
	call(["rm", ruta_cfg_aux])


################################################################
#---Funciones que modifican la configuracion de las maquinas---#
################################################################

#hostname: modifica el archivo hostname y lo envia a la maquina virtual 
def hostname(text):
	print("Archivo hostname de "+text+" comienza modificacion")
	ruta_vm_hostname="/etc/hostname";
	ruta_vm_hostname_reducida="/etc/";
	ruta_hostname=ruta_dir+"hostname"
	call(["touch",ruta_hostname]);
	#edito el hostname (en el host)
	fout=open(ruta_hostname,"w");
	fout.write(text+"\n");
	fout.close();
	#lo mando a la maquina virtual(del host a vm)
	call(["sudo", "virt-copy-in","-a", ruta_dir+text+".qcow2", ruta_hostname, ruta_vm_hostname_reducida])
	print("Archivo hostname de "+text+" modificado")

#hosts: descarga el archivo hosts de la maquina virtual, lo modifica y lo envia
def hosts(text):
	print("Archivo hosts de "+text+" comienza modificacion")
	ruta_vm_hosts="/etc/hosts";
	ruta_vm_hosts_reducida="/etc/";
	ruta_hosts=ruta_dir+"hosts"
	call(["touch",ruta_hosts]);
	ruta_aux=ruta_dir+"original/hosts";
	ruta_aux_reducida=ruta_dir+"original/";
	call(["mkdir",ruta_aux_reducida]);
	#copio el hosts (de vm a host)
	call(["sudo", "virt-copy-out","-a", ruta_dir+text+".qcow2", ruta_vm_hosts, ruta_aux_reducida])
	#edito el hosts (en el host)
	fin=open(ruta_aux,"r");
	fout=open(ruta_hosts,"w");
	for line in fin:
		if "127.0.1.1" in line:
			fout.write("127.0.1.1   "+text+"\n");
		else:
			fout.write(line);
	fin.close();
	fout.close();
	#lo mando a la maquina virtual(del host a vm)
	call(["sudo", "virt-copy-in","-a", ruta_dir+text+".qcow2", ruta_hosts, ruta_vm_hosts_reducida])
	borrarSilencioso(ruta_aux_reducida);
	print("Archivo hosts de "+text+" modificado")

#interfaces: descarga el archivo interfaces de la maquina virtual, lo modifica y lo envia
def interfaces(text):
	print("Archivo interfaces de "+text+" comienza modificacion")
	ruta_vm_interfaces="/etc/network/interfaces";
	ruta_vm_interfaces_reducida="/etc/network";
	ruta_interfaces=ruta_dir+"interfaces"
	call(["touch",ruta_interfaces]);
	ruta_aux=ruta_dir+"/original/interfaces";
	ruta_aux_reducida=ruta_dir+"/original/";
	call(["mkdir",ruta_aux_reducida]);
	#copio el fichero interfaces (de vm a host)
	call(["sudo", "virt-copy-out","-a", ruta_dir+text+".qcow2", ruta_vm_interfaces, ruta_aux_reducida])
	#edito el fichero interfaces (en el host)
	fin=open(ruta_aux,"r");
	fout=open(ruta_interfaces,"w");
	#si estamos modificando un servidor
	if (text[0]=="s"):
		n_serv_str=str(int(text[1])+10);#terminacion de la ip del servidor
	for line in fin:
		if "iface eth0 inet dhcp" in line:
			#fout.write(line)
			if (text=="c1"):
				fout.write("iface eth0 inet static\n")
				fout.write("address 10.0.1.2\n");
				fout.write("netmask 255.255.255.0\n");
				fout.write("gateway 10.0.1.1\n");
				fout.write("dns-nameservers 10.0.1.1\n");
			elif(text=="lb"):
				#primera interfaz de red
				fout.write("iface eth0 inet static\n")
				fout.write("address 10.0.1.1\n");
				fout.write("netmask 255.255.255.0\n\n");
				#segunda interfaz de red
				fout.write("auto eth1\n")
				fout.write("iface eth1 inet static\n")
				fout.write("address 10.0.2.1\n");
				fout.write("netmask 255.255.255.0\n");
			elif (text[0]=="s"):#sera un servidor
				fout.write("iface eth0 inet static\n")
				fout.write("address 10.0.2."+n_serv_str+"\n");
				fout.write("netmask 255.255.255.0\n");
				fout.write("gateway 10.0.2.1\n");
				fout.write("dns-nameservers 10.0.2.1\n");
		else:
			fout.write(line);
	fin.close();
	fout.close();
	#lo mando a la maquina virtual(del host a vm)
	call(["sudo", "virt-copy-in","-a", ruta_dir+text+".qcow2", ruta_interfaces, ruta_vm_interfaces_reducida])
	borrarSilencioso(ruta_aux_reducida);
	print("Archivo interfaces de "+text+" modificados")

#interfaces_ip_forward: descarga el archivo sysctl.conf del lb, lo modifica para que el lb pueda hacer de enrutador y lo envia
def interfaces_ip_forward():
	text="lb"
	print("Archivo sysctl.conf de lb comienza modificacion")
	ruta_vm_sysctl="/etc/sysctl.conf";
	ruta_vm_sysctl_reducida="/etc/";
	ruta_sysctl=ruta_dir+"sysctl.conf"
	call(["touch",ruta_sysctl]);
	ruta_aux=ruta_dir+"/original/sysctl.conf";
	ruta_aux_reducida=ruta_dir+"/original/";
	call(["mkdir",ruta_aux_reducida]);
	#copio el sysctl.conf (de vm a host)
	call(["sudo", "virt-copy-out","-a", ruta_dir+text+".qcow2", ruta_vm_sysctl, ruta_aux_reducida])
	#edito el hosts (en el host)
	fin=open(ruta_aux,"r");
	fout=open(ruta_sysctl,"w");
	for line in fin:
		if "#net.ipv4.ip_forward=1" in line:
			fout.write("net.ipv4.ip_forward=1 \n");
		else:
			fout.write(line);
	fin.close();
	fout.close();
	#lo mando a la maquina virtual(del host a vm)
	call(["sudo", "virt-copy-in","-a", ruta_dir+text+".qcow2", ruta_sysctl, ruta_vm_sysctl_reducida])
	borrarSilencioso(ruta_aux_reducida);
	print("Archivo sysctl.conf de "+text+" modificado")

#index: modifica el archivo index.html de cada servidor y lo envia a la maquina virtual
def index(server, html):
	ruta_index=ruta_dir+"index.html";
	ruta_vm_index_reducida="/var/www/html/";
	call(["touch",ruta_index]);
	f=open(ruta_index,"w");
	f.write(html);
	f.close();
	call(["sudo", "virt-copy-in","-a", ruta_dir+server+".qcow2", ruta_index, ruta_vm_index_reducida])
	print("Archivo index.html de "+server+" modificado")

#balancer: descarga el archivo haproxy.cfg de lb y le anyade las lineas necesarias para utilizarlo como balanceador de trafico
def balancer():
	n_serv=getNServ()+1;
	text="lb"
	print("Archivo haproxy.cfg de lb comienza modificacion")
	ruta_vm_haproxy="/etc/haproxy/haproxy.cfg";
	ruta_vm_haproxy_reducida="/etc/haproxy/";
	ruta_haproxy=ruta_dir+"haproxy.cfg"
	call(["touch",ruta_haproxy]);
	ruta_aux=ruta_dir+"/original/haproxy.cfg";
	ruta_aux_reducida=ruta_dir+"/original/";
	call(["mkdir",ruta_aux_reducida]);
	#copio el sysctl.conf (de vm a host)
	call(["sudo", "virt-copy-out","-a", ruta_dir+text+".qcow2", ruta_vm_haproxy, ruta_aux_reducida])
	#edito el hosts (en el host)
	fin=open(ruta_aux,"r");
	fout=open(ruta_haproxy,"w");
	for line in fin:
		if "errorfile 504 /etc/haproxy/errors/504.http" in line:
			#implementacion del round robin
			fout.write(line);
			fout.write("\n");
			fout.write("frontend lb\n");
			fout.write("	bind *:80\n");
			fout.write("	mode http\n");
			fout.write("	default_backend webservers\n");
			fout.write("");
			fout.write("backend webservers\n");
			fout.write("	mode http\n");
			fout.write("	balance roundrobin\n");
			for server in range(1,n_serv):
				fout.write("server s"+str(server)+" 10.0.2.1"+str(server)+":80 check\n");
			#implementacion de la visualizacion de estadisticas
			fout.write("listen stats\n");
			fout.write("	bind :8001\n");
			fout.write("	stats enable\n");
			fout.write("	stats uri /\n");
			fout.write("	stats hide-version\n");
			fout.write("	stats auth admin:cdps\n");
		else:
			fout.write(line);
	fin.close();
	fout.close();
	#lo mando a la maquina virtual(del host a vm)
	call(["sudo", "virt-copy-in","-a", ruta_dir+text+".qcow2", ruta_haproxy, ruta_vm_haproxy_reducida])
	borrarSilencioso(ruta_aux_reducida);
	print("Archivo haproxy.cfg de "+text+" modificado")
	
##########################################################################
#---------------Funciones que dibujan en el terminal---------------------#
##########################################################################

def bombaInicio():
	print("Has Activado el protocolo de destruccion")
	print("\33[5;31m")	
	print("			        *****    ");
	print("			        |        ");
	print("			        |        ");
	print("			    ____|____    ");
	print("			   /         \   ");
	print("			  /           \  ");
	print("			 /             \ ");
	print("			|----PRACTICA---|");
	print("			 \             / ");
	print("			  \           /  ");
	print("			   \_________/   "+"\33[m"+"\n");

def bombaFin():
	print("")
	print("                             \         .  .  /    ")
	print("                           \      ;:.:;.:..  /    ")
	print("                               (M^^.^~~:.'').     ")
	print("                         -   (/  .    . . \ \)  - ")
	print("  O                         ((| :. ~ ^  :. .|))   ")
	print(" |\                      -   (\- |  \ /  |  /)  - ")
	print(" |  T                         -\  \     /  /-     ")
	print("/ \[_]..........................\  \   /  /       "+"\n");

def bombaNuclear():
	print("\33[0;31m")
	print("                     __,-~~/~    `---.                             ")
	print("                   _/_,---(      ,    )                            ")
	print("               __ /        <    /   )  \___                        ") 
	print("- ------===;;;'====------------------===;;;===----- -  -           ")
	print("                  \/~~~~~(~~~~\~~)~~~~~~\/                         ")
	print("                  (_ (   \  (     >    \)                          ")
	print("                   \_( _ <         >_>'                            ")
	print("                      ~ `-i' ::>|--'                               ")
	print("                          I;|.|.|                                  ")
	print("                         <|i::|i|`.                                ")
	print("                        [` ^''`-' ]                                ")
	print("------------------------------------------------------------------ "+"\33[m"+"\n");

##########################################################################
#---------------------VALORES POR DEFECTO Y CONSTANTES-------------------#
##########################################################################

ruta_dir="/mnt/tmp/practica_creativa/"
ruta_cfg=ruta_dir+"pf1.cfg"

if len(sys.argv)>=2:
	orden=(sys.argv[1]).lower()
	print("\033[1;36m"+"Ha seleccionado la funcion de: "+orden+"\033[m");
else:
	print("\033[1;36m"+"Elija una orden: crear, arrancar, parar, stop_one, run_one, destruir o monitor"+"\033[m")	
	sys.exit()

#Variables de estado, se les asigna lo que hay en el fichero de configuracion
creado=getVarBool("creado");
arrancado=getVarBool("arrancado");
parado=getVarBool("parado");

##########################################################################
# -------------------------------CREAR-----------------------------------#
##########################################################################

if (orden == "crear") and (not(creado)):
	n_serv=2
	n_serv_for=n_serv+1
	
	call(["mkdir",ruta_dir]);
	call(["touch",ruta_cfg]);

#asignacion de numero de servidores	
	if len(sys.argv)>=3:
		n_serv=int(sys.argv[2])
		n_serv_for=n_serv+1
	print("Numero de servidores elegido = "+str(n_serv))
#comprobacion de rango servidores adecuado + escritura en el .cfg
	if ((n_serv<6) and (n_serv>0)):
		cfg=open(ruta_cfg, "w");
		cfg.write("num_serv="+ str(n_serv) + "\n")
		cfg.write("creado=1\n")
		cfg.write("arrancado=0\n")
		cfg.write("parado=0\n")
		cfg.close()
	else:
		print("\033[0;31m"+"ERROR numero de servidores fuera del rango"+"\033[m")
		borrarSilencioso(ruta_dir);
		sys.exit()

#copiamos las plantillas para C1 y LB
	print("Copiando plantillas a files")
	call(["cp", "plantilla-vm-pf1.xml", ruta_dir+"c1.xml"])
	call(["cp", "cdps-vm-base-pf1.qcow2", ruta_dir+"c1.qcow2"])
	print("Plantilla de c1 copiada")
	call(["cp", "cdps-vm-base-pf1.qcow2", ruta_dir+"lb.qcow2"])
	call(["cp", "plantilla-vm-pf1.xml", ruta_dir+"lb.xml"])
	print("Plantilla de lb copiada")

#copiamos las plantillas de los servidores
	for server in range(1,n_serv_for):
		call(["cp", "plantilla-vm-pf1.xml", ruta_dir+"s"+str(server)+".xml"])
		call(["cp", "cdps-vm-base-pf1.qcow2", ruta_dir+"s"+str(server)+".qcow2"])
		print("Plantilla de s"+str(server)+" copiada")

	print("\033[0;32m"+"Plantillas copiadas"+"\033[m")

#Edito la plantilla de c1
	print("Editando plantilla c1")
	fin = open("plantilla-vm-pf1.xml", "r");
	fout = open(ruta_dir+"c1.xml", "w");

	for line in fin:
		if "<name>XXX</name>" in line:
			fout.write("<name>c1</name>\n")
		elif "<source file='/mnt/tmp/XXX/XXX.qcow2'/>" in line: 
			fout.write("<source file='"+ruta_dir+"c1.qcow2'/>\n")
		elif "<source bridge='XXX'/>" in line:
			fout.write("<source bridge='LAN1'/>\n")
		else :
			fout.write(line)
	fin.close()
	fout.close()

#Edito la plantilla de lb
	print("Editando plantilla lb")
	fin = open("plantilla-vm-pf1.xml", "r");
	fout = open(ruta_dir+"lb.xml", "w");

	for line in fin:
		if "<name>XXX</name>" in line:
			fout.write("<name>lb</name>\n")
		elif "<source file='/mnt/tmp/XXX/XXX.qcow2'/>" in line: 
			fout.write("<source file='"+ruta_dir+"lb.qcow2'/>\n")
		elif "<source bridge='XXX'/>" in line:
			fout.write("<source bridge='LAN1'/>\n")
		elif "</interface>" in line:
			fout.write(line)
			fout.write("<interface type='bridge'>\n<source bridge='LAN2'/>\n<model type='virtio'/>\n</interface>\n")
		else :
			fout.write(line)
	fin.close()
	fout.close()

#Edito las plantillas de los servidores
	for server in range(1,n_serv_for):
		print("Editando plantilla s"+str(server))
		fin = open("plantilla-vm-pf1.xml", "r");
		fout = open(ruta_dir+"s"+str(server)+".xml", "w");
	
		for line in fin:
			if "<name>XXX</name>" in line:
				fout.write("<name>s"+str(server)+"</name>\n")
			elif "<source file='/mnt/tmp/XXX/XXX.qcow2'/>" in line: 
				fout.write("<source file='"+ruta_dir+"s"+str(server)+".qcow2'/>\n")
			elif "<source bridge='XXX'/>" in line:
				fout.write("<source bridge='LAN2'/>\n")
			else :
				fout.write(line)
		fin.close()
		fout.close()

	print("\033[0;32m"+"Plantillas editadas"+"\033[m")

#crear bridges
	call(["sudo", "brctl", "addbr", "LAN1"])
	call(["sudo", "brctl", "addbr", "LAN2"])
	call(["sudo", "ifconfig", "LAN1", "up"])
	call(["sudo", "ifconfig", "LAN2", "up"])
	print("\033[0;32m"+"Bridges establecidos"+"\033[m")

#editar ficheros en la VM
#editar el hostname
	hostname("c1");
	hostname("lb");
	for server in range(1,n_serv_for):
		hostname("s"+str(server));
#editar el hosts
	hosts("c1");
	hosts("lb");
	for server in range(1,n_serv_for):
		hosts("s"+str(server));

#editar interfaces
	interfaces("c1");
	interfaces("lb");
	interfaces_ip_forward();
	balancer();#configuracion del balanceador de carga
	for server in range(1,n_serv_for):
		interfaces("s"+str(server));
	#ademas de ejecutar los comandos en el host 
	call(["sudo", "ifconfig", "LAN1", "10.0.1.3/24"])
	call(["sudo", "ip", "route", "add", "10.0.0.0/16", "via", "10.0.1.1"])

#editar los htmls
	for server in range(1,n_serv_for):
		index("s"+str(server), "Pagina del servidor s"+str(server));

#definir maquinas
	call(["sudo", "virsh", "define",ruta_dir+"c1.xml"])
	call(["sudo", "virsh", "define",ruta_dir+"lb.xml"])
	for server in range(1,n_serv_for):
		call(["sudo", "virsh", "define",ruta_dir+"s"+str(server)+".xml"])
	print("\033[0;32m"+"Ficheros de configuracion de red editados"+"\033[m"+"\n");	
	print("\033[5;32m"+"ENTORNO CREADO"+"\033[m")

elif (orden == "crear") and (creado):
	print("\033[0;33m"+"El entorno ya esta creado"+"\033[m");

##########################################################################
# -------------------------------ARRANCAR--------------------------------#
##########################################################################

if (orden == "arrancar") and (creado) and (not(arrancado)):
	n_serv_for = getNServ()+1;
	setVarBool("arrancado",1)
	setVarBool("parado",0)	

#arrancar maquinas
	call(["sudo", "virsh", "start","c1"])
	call(["sudo", "virsh", "start","lb"])
	for server in range(1,n_serv_for):
		call(["sudo", "virsh", "start","s"+str(server)])

#Abrir terminales
	cmd_c1='sudo virsh console c1';
	subprocess.Popen(["xterm","-title", "c1", "-e", cmd_c1 ])
	cmd_lb='sudo virsh console lb';
	subprocess.Popen(["xterm","-title", "lb", "-e", cmd_lb ])
	for server in range(1,n_serv_for):
		cmd_s='sudo virsh console s'+str(server);
		subprocess.Popen(["xterm","-title", "s"+str(server), "-e", cmd_s ])
	print("\033[5;32m"+"MAQUINAS INICIADAS"+"\033[m");

elif (orden == "arrancar") and (arrancado):
	print("\033[0;33m"+"El entorno ya esta arrancado"+"\033[m");
elif (orden == "arrancar") and (not(creado)):
	print("\033[0;33m"+"No hay ningun entorno creado"+"\033[m");

##########################################################################
# -------------------------------PARAR-----------------------------------#
##########################################################################
if (orden == "parar") and (arrancado):
	n_serv_for = getNServ()+1;
	setVarBool("parado",1)
	setVarBool("arrancado",0)
	try:	
		call(["sudo", "virsh", "shutdown", "c1"])
		print("Maquina c1 parada\n");
		call(["sudo", "virsh", "shutdown", "lb"])
		print("Maquina lb parada\n");	
		n_serv_for = getNServ()+1;
		for server in range(1,n_serv_for):
			call(["sudo", "virsh", "shutdown","s"+str(server)])
			print("Maquina s"+str(server)+ " parada\n");
		print("\033[0;32m"+"MAQUINAS PARADAS"+"\033[m");
	except:
		print("La maquina ya esta parada");	
	
elif (orden == "parar"):
	print("\033[0;33m"+"No hay ningun entorno arrancado"+"\033[m");

##########################################################################
# ----------------------PARAR MAQUINAS INDIVIDUALMENTE-------------------#
##########################################################################

if (orden == "stop_one"):
	try:		
		machine= sys.argv[2];
	except:
		print("\033[1;33m"+"Se requiere un argumento"+"\033[m")
		sys.exit();
	try:
		n_serv_for = getNServ()+1;
	except:
		print("\033[1;33m"+"Primero debes crear el entorno"+"\033[m");
		sys.exit();		
	try:
		if (machine=="c1") or (machine=="lb") or (int(machine[1])<(n_serv_for)):
			try:	
				call(["sudo", "virsh", "shutdown", machine])
				print("\033[0;32m"+"Maquina "+machine+" parada\n"+"\033[m");
			except:
				print("\033[0;33m"+"La maquina ya esta parada"+"\033[m");
				sys.exit();
		else: 
			print("\033[1;31m"+"La maquina no existe"+"\033[m")
	except:
		print("\033[1;31m"+"Argumento invalido"+"\033[m");

##########################################################################
# -------------------ARRANCAR MAQUINAS INDIVIDUALMENTE-------------------#
##########################################################################

if (orden == "run_one"):
	try:		
		machine= sys.argv[2];
	except:
		print("\033[1;33m"+"Se requiere un argumento"+"\033[m")
		sys.exit();
	try:
		n_serv_for = getNServ()+1;
	except:
		print("\033[1;33m"+"Primero debes crear el entorno"+"\033[m");
		sys.exit();
	try:
		if (machine=="c1") or (machine=="lb") or (int(machine[1])<(n_serv_for)):
			try:	
				call(["sudo", "virsh", "start", machine])
				cmd='sudo virsh console '+machine;
				subprocess.Popen(["xterm","-title", machine, "-e", cmd ])
				print("\033[0;32m"+"Maquina "+machine+" arrancada\n"+"\033[m");
			except:
				print("\033[1;33m"+"La maquina ya esta arrancada"+"\033[m");
				sys.exit();
		else: 
			print("\033[1;31m"+"La maquina no existe"+"\033[m")
	except:
		print("\033[1;31m"+"Argumento invalido"+"\033[m");	

##########################################################################
# ------------------------------DESTRUIR---------------------------------#
##########################################################################
if (orden == "destruir") and (creado): 
	bombaInicio();
	call(["sudo", "virsh", "undefine", "c1"])
	call(["sudo", "virsh", "destroy", "c1"])
	call(["sudo", "virsh", "undefine", "lb"])
	call(["sudo", "virsh", "destroy", "lb"])	
	n_serv_for = getNServ()+1;
	for server in range(1,n_serv_for):
		call(["sudo", "virsh", "undefine","s"+str(server)])
		call(["sudo", "virsh", "destroy","s"+str(server)])
	print("\033[0;32m"+"Maquinas Eliminadas""\033[m")

	call(["sudo","ifconfig","LAN1","down"])
	call(["sudo","ifconfig","LAN2","down"])
	call(["sudo","brctl","delbr","LAN1"])
	call(["sudo","brctl","delbr","LAN2"])
	print("\033[0;32m"+"Brigdes eliminados"+"\033[m")

	borrar(ruta_dir)
	#no es necesario porque se borra el archivo de configuracion
	'''setVarBool("creado",0)
	setVarBool("arrancado",0)
	setVarBool("parado",0)'''
	bombaFin();

elif (orden == "destruir"):
	print("\033[0;33m"+"No hay ningun entorno creado"+"\033[m");

##########################################################################
# ------------------------------MONITORIZACION---------------------------#
##########################################################################

if(orden == "monitor")and (arrancado):
	try:		
		arg = sys.argv[2];
	except:
		print("\033[0;33m"+"Seleccione el modo de monitor: ping, watch, list o balance-stats"+"\033[m")
		sys.exit();


	if arg=="ping":
		if len(sys.argv)<4:
			print("\033[0;33m"+"Introduzca nombre de maquina a la que hacer el ping"+"\033[m");
			sys.exit();	
		else:
			maquina=sys.argv[3];

		if maquina=="c1":
			direccion_ip="10.0.1.2"
			call(["ping","-c","3",direccion_ip])
		elif maquina=="lb":
			direccion_ip="10.0.1.1"
			call(["ping","-c","3",direccion_ip])
			print("")
			direccion_ip="10.0.2.1"
			call(["ping","-c","3",direccion_ip])
		elif maquina[0] == "s":
			try:
				direccion_ip="10.0.2.1"+maquina[1];
				call(["ping","-c","3",direccion_ip]);
			except:
				print("\033[1;31m"+"La maquina no existe"+"\033[m")
		else:
			print("\033[1;31m"+"La maquina no existe"+"\033[m")
			sys.exit();

	elif arg=="watch":
		#comprobacion de parametros
		if len(sys.argv)<4:
			print("\033[0;33m"+"Introduzca nombre de maquina deseada"+"\033[m");
			sys.exit();	
		else:
			maquina=sys.argv[3];

		if maquina!="c1" and maquina!="lb" and maquina[0]!="s":
			print("\033[1;31m"+"La maquina no existe"+"\033[m")
			sys.exit();
		elif maquina[0]=="s":
			try:
				id_server=int(maquina[1]);
				comp=id_server<=getNServ();
			except:
				print("\033[1;31m"+"Nombre de maquina no valido"+"\033[m");
				sys.exit();

			if not(comp):
				print("\033[1;31m"+"Nombre de maquina no valido"+"\033[m");
				sys.exit();
		#ejecucion de comandos
		cmd_m='watch sudo virsh cpu-stats '+maquina;
		subprocess.Popen(["xterm","-title", "Monitor "+maquina, "-e", cmd_m ]);
		print("\033[1;32m"+"Abierto monitor de uso de CPU de "+maquina+"\033[m")

	elif arg=="list":
		call(["sudo", "virsh", "list"]);

	elif arg=="balance-stats":
		call(["/usr/bin/firefox","-new-window","http://10.0.1.1:8001/"]);
		print("\033[1;32m"+"Abierta pagina de estadisticas de HAProxy"+"\033[m")
		#para probar el balanceador de carga introducir "watch -n 0.5 curl 10.0.1.1"
		#o "while true; do curl 10.0.1.1; sleep 0.1; done"

	else:
		print("\033[1;31m"+"Inserte una opcion de monitor valida: ping, watch, list o balance-stats"+"\033[m")

elif (orden == "monitor"):
	print("\033[0;33m"+"Para monitorizar el entorno debe estar arrancado"+"\033[m");

	
#Si la orden no es adecuada
if (orden != "crear") and (orden != "arrancar") and (orden != "parar") and (orden != "destruir") and (orden != "monitor") and (orden != "balance") and (orden!="stop_one") and (orden!="run_one"):
	print("\033[1;31m"+"La orden seleccionada no existe"+"\033[m")
	





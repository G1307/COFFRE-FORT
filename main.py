#!/usr/bin/env python
import os
import base64
import shutil
import pyAesCrypt
from subprocess import call
from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class secret_vault:
	
	buffer_size = 64 * 1024

	def __init__(self, masterpwd):
		self.masterpwd = masterpwd

	def add_file(self, path, encrypt):
		if encrypt:
			filenameWithExt = os.path.basename(path) + '.aes'
			vaultpath = self.hid_dir + filenameWithExt
			pyAesCrypt.encryptFile(path, vaultpath, self.key.decode(), self.buffer_size)
		else:
			shutil.copy(path, self.hid_dir)

	def del_file(self, index):
		filenameWithExt = self.files[index]
		vaultpath = self.hid_dir + filenameWithExt
		if filenameWithExt.endswith('.aes'):
			filename = filenameWithExt[:-4]
			pyAesCrypt.decryptFile(vaultpath, filename, self.key.decode(), self.buffer_size)
			os.remove(vaultpath)
		else:
			shutil.copy(vaultpath, filenameWithExt)
			os.remove(vaultpath)

	def list_files(self):
		self.get_files()
		if not self.files:
			print("\nVault is empty!!!")
			return
		maxlen = max([len(x) for x in self.files])
		print('')
		print('-'*(maxlen+10))
		print("index\t|files")
		print('-'*(maxlen+10))
		for i, file in enumerate(self.files):
			print("{}\t|{}".format(i, file))
			print('-'*(maxlen+10))

	def generate_key(self, salt=b"\xb9\x1f|}'S\xa1\x96\xeb\x154\x04\x88\xf3\xdf\x05", length=32):
	    password = self.masterpwd.encode()
	    
	    kdf = PBKDF2HMAC(algorithm = hashes.SHA256(),
	                     length = length,
	                     salt = salt,
	                     iterations = 100000,
	                     backend = default_backend())
	    
	    self.key = base64.urlsafe_b64encode(kdf.derive(password))

	def get_files(self):
		self.files = os.listdir(self.hid_dir)

	def set_hid_dir(self):
		path = '~/.vault'
		hid_path = os.path.expanduser(path)
		self.hid_dir = hid_path + '/'

def main():
	print("Bienvenu dans votre coffre fort!!!")
	path = os.path.expanduser('~/.vaultcfg')
	if os.path.exists(path):
		masterpwd = getpass("Entrer votre mot de passe : ")
		vault = secret_vault(masterpwd)
		vault.generate_key()
		fernet = Fernet(vault.key)
		with open(path, 'rb') as f:
			actual_mpwd = f.read()
			try:
				fernet.decrypt(actual_mpwd)
				print('Welcome Back')
			except:
				print("Wrong Password!")
				exit()
	else:
		masterpwd = getpass("Créer un mot de passe : ")
		vault = secret_vault(masterpwd)
		vault.generate_key()
		fernet = Fernet(vault.key)
		enc_mpwd = fernet.encrypt(masterpwd.encode())
		with open(path, 'wb') as f:
			f.write(enc_mpwd)
			vault.set_hid_dir()
		try:
			os.makedirs(vault.hid_dir[:-1])
		except FileExistsError:
			pass

		if os.name == 'nt':
			call(["attrib", "+H", vault.hid_dir[:-1]])
			call(["attrib", "+H", path])

		print("Bienvenu")

	vault.set_hid_dir()

	choice = 0
	while choice != 4:
		print("\nEnter 1 pour archiver un fichier\nEnter 2 pour désarchiver un fichier\nEnter 3 pour voir votre coffre-fort\nEnter 4  Exit\nEnter 5 pour réinitialiser le coffre-fort et supprimer tout son contenu\n")
		try:
			choice = int(input("Enter votre choix : "))
		except:
			print("\nvaleur inconnu!")
			continue

		if choice == 1:
			print("\nTip : Faites glisser et déposez le fichier")
			filepath = input("Saisissez le chemin du fichier à masquer : ")
			filepath = filepath.replace('\\', '')
			if filepath.endswith(' '):
				filepath = filepath[:-1]
			if os.path.exists(filepath):
				if os.path.isfile(filepath):
					while True:
						enc_or_not = input("Voulez-vous chiffrer le fichier ? (Y or N) : ")
						if enc_or_not == 'y' or enc_or_not == 'Y':
							print('\nAjout du fichier au coffre-fort...')
							vault.add_file(filepath, 1)
							print("\nFichier ajouté avec succès au coffre-fort")
							print("Vous pouvez maintenant supprimer le fichier d'origine si vous le souhaitez")
							break
						elif enc_or_not == 'n' or enc_or_not == 'N':
							print('\nAjout du fichier au coffre-fort...')
							vault.add_file(filepath, 0)
							print("\nFichier ajouté avec succès au coffre-fort")
							print("Vous pouvez maintenant supprimer le fichier d'origine si vous le souhaitez")
							break
						else:
							print("Taper Y ou N")
				else:
					print("\nLe chemin donné est un répertoire et non un fichier!")
			else:
				print('\nLe fichier n existe pas !')

		elif choice == 2:
			print('')
			try:
				file = int(input("Entrez l'index du fichier à partir de cofrt-fort : "))
				vault.del_file(file)
				print('\nFile désarchivé avec succès')
				print('Le fichier sera présent dans {}'.format(os.getcwd()))
			except:
				print("\nIndice invalide !")

		elif choice == 3:
			vault.list_files()

		elif choice == 5:
			while True:
				confirm = input("\nVoulez-vous vraiment supprimer et réinitialiser le coffre-fort?(Y or N) : ")
				if confirm == 'y' or confirm == 'Y':
					pwdCheck = getpass("\nEnter le mot de passe pour confirmer : ")
					reset = secret_vault(pwdCheck)
					reset.generate_key()
					resetFernet = Fernet(reset.key)
					path = os.path.expanduser('~/.vaultcfg')
					with open(path, 'rb') as f:
						actual_mpwd = f.read()
						try:
							resetFernet.decrypt(actual_mpwd)
							print('Suppression et réinitialisation de toutes les données...')
						except Exception as e:
							print(e)
							print("\nWrong Password!")
							print("Fermeture du programme maintenant...")
							exit()
					os.remove(path)
					shutil.rmtree(vault.hid_dir[:-1])
					print('\nRéinitialisation effectuée. Merci')
					exit()
				elif confirm == 'n' or confirm == 'N':
					print("\nHappy for that")
					break
				else:
					print("Type Y or N")


if __name__ == '__main__':
	main()

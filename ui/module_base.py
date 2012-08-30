
from PySide import QtGui, QtCore,QtUiTools
from threading import Thread
from Queue import Queue

#Base class for GUI modules that abstracts away some of the setup
class module_base(QtGui.QDialog):
    #Imported_files list of the files that have been inported
    #ui_file the pyside .ui file to build the GUI for the module
    def __init__(self,imported_files,generated_lc,ui_file):
        super(module_base,self).__init__()
        self.files = imported_files
        self.gen_files = generated_lc
    
        #load the UI file
        file = QtCore.QFile(ui_file)
        file.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.window = loader.load(file,self)
        
        file.close()
      
        self.window.btnCncl.clicked.connect(self.window.close)
        self.window.btnOk.clicked.connect(self._Ok_pressed)
        
        self.selected_file=''

        self.lc = None
        self.window.progressBar.setVisible(False)
        self.window.progressBar.setTextVisible(False)
    
    def mbox_error(self, string):
        msgBox = QtGui.QMessageBox()
        msgBox.setText(string)
        msgBox.setWindowTitle('Error')
        msgBox.setIcon(QtGui.QMessageBox.Critical) 
        msgBox.exec_()        

    def _set_button_enabled(self,state):
        self.window.btnCncl.setEnabled(state)
        self.window.btnOk.setEnabled(state)
        
    #return the selected file before handing off to the 'user' function
    def _Ok_pressed(self):

        file = self.window.filelist.currentText()
        idx = file.find('[')
        if idx != -1:
            file = file[0:idx].rstrip()
        self.selected_file = None
        #look for the file in imported files
        for f in self.files:
            if f == file:
                self.selected_file = self.files[f]
        
        if self.selected_file == None:
            #let's try the user generated files
            for f in self.gen_files:
                if f == file:
                    self.selected_file = self.gen_files[f]                
        
        if self.selected_file  == None:
            self.mbox_error('Could not find the selected file')
            return

        kwargs = self.init_run()
        
        #bail if we have garbage
        if kwargs == None:
            return
        
        self.window.progressBar.setVisible(True)
        self.window.progressBar.setRange(0,0)
        self.window.progressBar.reset#so it actually appears...        
        self._set_button_enabled(False)
        q = Queue()
        def run_exec_module(q,**kwargs):
            q.put(self.exec_module(**kwargs))
        t = Thread(target=run_exec_module,args=(q,),kwargs=kwargs)
        t.start()
        while t.isAlive():
            QtGui.QApplication.processEvents()
        t.join()
        self.lc = q.get()
     

        #self.lc =  self.run()
        self.window.progressBar.setVisible(False)
        self._set_button_enabled(True)
        if self.lc:
            self.window.close()
    
    #setup the ui and then show it
    def show_ui(self):
        #setup the file list
        self.window.filelist.clear()
        for f in self.files:
            self.window.filelist.addItem( f + '  [' + self.files[f].get_path()+']' )      
            self.window.filelist.addItem('--------')
        for f in self.gen_files:
            self.window.filelist.addItem(f)
            
        self.window.setWindowTitle(self.name + ' - ' + str(self.version))
        #show the window
        self.window.exec_()

        return self.lc

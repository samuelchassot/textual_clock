//
//  SettingsView.swift
//  textual_clock_companion
//
//  Created by Samuel Chassot on 08.02.23.
//

import SwiftUI

struct SettingsView: View {
    @Environment(\.managedObjectContext) var managedObjectContext
    @State private var clock_address = ""
    @State private var clock_port = ""
    @State private var showAlertSaved = false
    @ObservedObject var keyboard = KeyboardResponder()
    var body: some View {
        NavigationView{
            
            VStack{
                Form{
                    Section(header: Text("Settings")){
                        HStack{
                            Text("Clock address")
                            Divider()
                            TextField("Clock address", text: self.$clock_address)
                                .submitLabel(.done)
                                .keyboardType(.default)
                                .disableAutocorrection(true)
                                .autocapitalization(.none)
                                .onSubmit {
                                    self.endEditing()
                                }
                        }
                        HStack{
                            Text("Clock port")
                            Divider()
                            TextField("Clock port", text: self.$clock_port)
                                .submitLabel(.done)
                                .keyboardType(.numberPad)
                                .disableAutocorrection(true)
                                .autocapitalization(.none)
                                .onSubmit {
                                    self.endEditing()
                                }
                        }
                    }
                    
                }
            }.navigationBarTitle("Settings")
        }.onAppear{
            self.loadSettings()
                    }
        .onTapGesture {
            self.endEditing()
        }
    }
    
    private func loadSettings() {
        let clockSettings = ClockSettingsUtility.getClockSettings(managedObjectContext: self.managedObjectContext)!
        self.clock_address = clockSettings.clock_name ?? ""
        self.clock_port = clockSettings.clock_port ?? ""
    }
    
    private func closeSettings() {
        
    }
    private func saveSettings(){
        var stringDict = Dictionary<ClockSettingsStringValues, String>()
        stringDict[.clock_name] = self.clock_address
        stringDict[.clock_port] = self.clock_port
        _ = ClockSettingsUtility.updateClockSettingsFromDicts(managedObjectContext: self.managedObjectContext, newClockSettingsDictStringAttributes: stringDict)
        self.loadSettings()
        self.showAlertSaved = true
    }
    
    func endEditing(){
        let keyWindow = UIApplication.shared.connectedScenes
            .filter({$0.activationState == .foregroundActive})
            .map({$0 as? UIWindowScene})
            .compactMap({$0})
            .first?.windows
            .filter({$0.isKeyWindow}).first
        keyWindow?.endEditing(true)
        saveSettings()
    }
}

struct SettingsViews_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
    }
}

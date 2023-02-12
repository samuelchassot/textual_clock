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
    @State private var connectionTestState = ConnectionTestState.base
    
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
                Spacer()
                Button(action: self.testConnection){
                    if(self.connectionTestState == .success){
                        Image(systemName: "checkmark")
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .frame(width: 300, height: 50)
                            .background(Color.green)
                            .cornerRadius(15)
                    } else if(self.connectionTestState == .failure){
                        Image(systemName: "xmark")
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .frame(width: 300, height: 50)
                            .background(Color.red)
                            .cornerRadius(15)
                    } else if (self.connectionTestState == .loading){
                        Image(systemName: "arrow.2.circlepath")
                            .resizable()
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .frame(width: 50, height: 50)
                            .background(Color.accentColor)
                            .cornerRadius(15)
                            .rotationEffect(.degrees(360))
                    }else{
                        Text("Test connection")
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .frame(width: 300, height: 50)
                            .background(Color.accentColor)
                            .cornerRadius(15)
                    }
                }
                Spacer()
            }.navigationBarTitle("Settings")
        }.onAppear{
            self.loadSettings()
                    }
        .onTapGesture {
            self.endEditing()
        }
    }
    
    private func testConnection(){
        self.connectionTestState = .loading
        let clockAddress = self.clock_address + ":" + self.clock_port
        HttpClockApiUtility.checkLiveness(clockAddress: clockAddress, onSuccess: {(msg) in
            self.showTestState(temporary_state: .success)
        }, onError: {(errorMsg) in
            print("error")
            self.showTestState(temporary_state: .failure)
        })
    }
    
    private func showTestState(temporary_state: ConnectionTestState){
        self.connectionTestState = temporary_state
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.connectionTestState = .base
        }
    }
    private func loadSettings() {
        let clockSettings = ClockSettingsUtility.getClockSettings(managedObjectContext: self.managedObjectContext)!
        self.clock_address = clockSettings.clock_name ?? ""
        self.clock_port = clockSettings.clock_port ?? ""
    }
    
    private func saveSettings(){
        var stringDict = Dictionary<ClockSettingsStringValues, String>()
        stringDict[.clock_name] = self.clock_address
        stringDict[.clock_port] = self.clock_port
        _ = ClockSettingsUtility.updateClockSettingsFromDicts(managedObjectContext: self.managedObjectContext, newClockSettingsDictStringAttributes: stringDict)
        self.loadSettings()
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
    
    enum ConnectionTestState{
        case base;
        case loading;
        case success;
        case failure;
    }
}

struct SettingsViews_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
    }
}

//
//  MainView.swift
//  textual_clock_companion
//
//  Created by Samuel Chassot on 08.02.23.
//

import SwiftUI

struct MainView: View {
    @Environment(\.managedObjectContext) private var viewContext
    
    @State private var selectedColor =
    Color(.sRGB, red: 0.98, green: 0.9, blue: 0.2)
    
    @State private var clockAddress = "raspberry"
    
    @State private var showSettings = false
    
    @State private var applyColorState = RequestState.base
    @State private var rebootState = RequestState.base
    
    var body: some View {
        NavigationView {
            VStack{
                Spacer()
                Text("Clock address: " + clockAddress)
                Spacer()
                Text("Select a color for the clock's text:")
                    .font(.headline)
                ColorPicker("Clock color", selection: $selectedColor)
                    .scaleEffect(CGSize(width: 2, height: 2))
                    .labelsHidden()
                    .padding([.top, .leading, .trailing])
                
                Spacer()
                
                Button(action: self.updateColorButton){
                    if(self.applyColorState == .success){
                        Image(systemName: "checkmark")
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .frame(width: 300, height: 50)
                            .background(Color.accentColor)
                            .cornerRadius(15)
                    } else if(self.applyColorState == .failure){
                        Image(systemName: "xmark")
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .frame(width: 300, height: 50)
                            .background(Color.accentColor)
                            .cornerRadius(15)
                    } else if (self.applyColorState == .loading){
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
                        Text("Apply color")
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .frame(width: 300, height: 50)
                            .background(Color.accentColor)
                            .cornerRadius(15)
                    }
                    
                    
                }
                Button(action: reboot){
                    if(self.rebootState == .success){
                        Image(systemName: "checkmark")
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .frame(width: 300, height: 50)
                            .background(.red)
                            .cornerRadius(15)
                    } else if(self.rebootState == .failure){
                        Image(systemName: "xmark")
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .frame(width: 300, height: 50)
                            .background(.red)
                            .cornerRadius(15)
                    } else if (self.rebootState == .loading){
                        Image(systemName: "arrow.2.circlepath")
                            .resizable()
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .frame(width: 50, height: 50)
                            .background(.red)
                            .cornerRadius(15)
                            .rotationEffect(.degrees(360))
                    }else{
                        Text("Reboot")
                            .font(.headline)
                            .foregroundColor(.white)
                            .padding()
                            .frame(width: 300, height: 50)
                            .background(.red)
                            .cornerRadius(15)
                    }
                }
                Spacer()
            }
            .navigationBarTitle("Textual Clock")
            .onAppear{
                self.loadClockName()
                self.getCurrentClockColor()
            }
        }
    }
    
    private func reboot(){
        HttpClockApiUtility.sendRebootCommand(clockAddress: self.clockAddress, onSuccess: {(msg) in
            self.showRebootState(temporary_state: .success)
        }, onError: {(errorMsg) in
            print("error")
            self.showRebootState(temporary_state: .failure)
        })
    }
    
    private func updateColorButton(){
        self.updateColor(color: self.selectedColor)
    }
    
    private func updateColor(color: Color) -> Void{
        print("update")
        let rgbColor = RgbColor.fromUIColor(uiColor: color)
        self.applyColorState = .loading
        HttpClockApiUtility.sendColorUpdate(clockAddress: self.clockAddress, color: rgbColor, onSuccess: {(msg) in
            self.showApplyColorResult(temporary_state: .success)
        }, onError: {(errorMsg) in
            print("error")
            self.showApplyColorResult(temporary_state: .failure)
        })
    }
    
    private func showApplyColorResult(temporary_state: RequestState){
        self.applyColorState = temporary_state
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.applyColorState = .base
        }
    }
    private func showRebootState(temporary_state: RequestState){
        self.rebootState = temporary_state
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.rebootState = .base
        }
    }
    
    
    private func getCurrentClockColor(){
        HttpClockApiUtility.getCurrentColor(clockAddress: self.clockAddress, onSuccess: {(rgbColor) in
            self.selectedColor = RgbColor.toUIColor(rgbColor: rgbColor)
        }, onError: {(errorMsg) in
            self.selectedColor = Color(.sRGB, red: 0.98, green: 0.9, blue: 0.2)
        })
    }
    
    private func loadClockName(){
        let clockSettings = ClockSettingsUtility.getClockSettings(managedObjectContext: viewContext)!
        let clockName = clockSettings.clock_name ?? "unset"
        let clockPort = clockSettings.clock_port ?? "unset"
        self.clockAddress = clockName + ":" + clockPort
    }
    
    enum RequestState{
        case base
        case loading
        case success
        case failure
    }
}

struct MainView_Previews: PreviewProvider {
    static var previews: some View {
        MainView()
    }
}

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
    
    @State private var selectedBrightness = 1.0 //between 0.0 and 1.0
    
    @State private var clockAddress = "raspberry"
    
    @State private var showSettings = false
    
    @State private var applyColorState = RequestState.base
    @State private var rebootState = RequestState.base
    
    @State private var styleOptions: [String] = []
    @State private var selectedStyle: String = ""
    
    var body: some View {
        NavigationView {
            VStack{
                Spacer()
                
                Text("Select a color for the clock's text:")
                    .font(.headline)
                ColorPicker("Clock color", selection: $selectedColor)
                    .scaleEffect(CGSize(width: 2, height: 2))
                    .labelsHidden()
                    .padding([.top, .leading, .trailing])
                Spacer()
                Text("Select a brightness:")
                Slider(value: $selectedBrightness, in: 0.0...1.0) {
                    Text("")
                } minimumValueLabel: {
                    Text("0%")
                } maximumValueLabel: {
                    Text("100%")
                }.frame(width: 250)
                Spacer()
                Text("Select a transition style:")
                if !styleOptions.isEmpty {
                    Picker("Update Style", selection: $selectedStyle) {
                        ForEach(styleOptions, id: \.self) { opt in
                            Text(opt.capitalized).tag(opt)
                        }
                    }
                    .pickerStyle(.menu)
                    .padding()
                }
                Spacer()
                
                
                Button(action: self.applyChanges){
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
                        Text("Apply Changes")
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
                self.getStyleOptions()
                self.getCurrentStyle()
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
    
    private func applyChanges() {
        let rgbColor = RgbColor.fromUIColor(uiColor: self.selectedColor).applyBrightness(brightness: selectedBrightness)
        self.applyColorState = .loading
        HttpClockApiUtility.sendColorUpdate(clockAddress: self.clockAddress, color: rgbColor, onSuccess: { _ in
            HttpClockApiUtility.postUpdateStyle(styleName: self.selectedStyle, onSuccess: { _ in
                self.showApplyColorResult(temporary_state: .success)
                self.getCurrentClockColor()
                self.getCurrentStyle()
            }, onError: { _ in
                self.showApplyColorResult(temporary_state: .failure)
            })
        }, onError: { _ in
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
            self.selectedBrightness = 1.0
        }, onError: {(errorMsg) in
            self.selectedBrightness = 1.0
            self.selectedColor = Color(.sRGB, red: 0.98, green: 0.9, blue: 0.2)
        })
    }
    
    private func loadClockName(){
        let clockSettings = ClockSettingsUtility.getClockSettings(managedObjectContext: viewContext)!
        let clockName = clockSettings.clock_name ?? "unset"
        let clockPort = clockSettings.clock_port ?? "unset"
        self.clockAddress = clockName + ":" + clockPort
    }
    
    private func getStyleOptions() {
        HttpClockApiUtility.getUpdateStyleOptions(onSuccess: { options in
            DispatchQueue.main.async {
                self.styleOptions = options
                if self.selectedStyle.isEmpty, let first = options.first {
                    self.selectedStyle = first
                }
            }
        }, onError: { _ in })
    }
    
    private func getCurrentStyle() {
        HttpClockApiUtility.getUpdateStyle(clockAddress: self.clockAddress, onSuccess: { style in
            DispatchQueue.main.async { self.selectedStyle = style }
        }, onError: { _ in })
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


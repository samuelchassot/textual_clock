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
                Button(action: reboot){
                    Text("Apply color")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                        .frame(width: 300, height: 50)
                        .background(Color.accentColor)
                        .cornerRadius(15)
                }
                Button(action: reboot){
                    Text("Reboot")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding()
                        .frame(width: 300, height: 50)
                        .background(.red)
                        .cornerRadius(15)
                }
                Spacer()
            }
            .navigationBarTitle("Textual Clock")
            .onAppear{
                self.loadClockName()}
        }
    }
    
    private func reboot(){
        
    }
    
    private func updateColor(color: Color){
        let arrRgb = UIColor(self.selectedColor).cgColor.components!
        let rgbColor = RgbColor(color_r: arrRgb[0], color_g: arrRgb[1], color_b: arrRgb[2])
        HttpClockApiUtility.sendColorUpdate(clockAddress: self.clockAddress, color: rgbColor, onSuccess: {(msg) in
            // TODO
        }, onError: {(errorMsg) in
            // TODO
        })
    }
    
    private func getCurrentClockColor(){
        HttpClockApiUtility.getCurrentColor(clockAddress: self.clockAddress, onSuccess: {(rgbColor) in
            self.selectedColor = Color(red: rgbColor.color_r, green: rgbColor.color_g, blue: rgbColor.color_b)
        }, onError: {(errorMsg) in
            self.selectedColor = Color(.sRGB, red: 0.98, green: 0.9, blue: 0.2)
        })
    }
    
    private func loadClockName(){
        let clockSettings = ClockSettingsUtility.getClockSettings(managedObjectContext: viewContext)!
        self.clockAddress = clockSettings.clock_name ?? "unset"
    }
}

struct MainView_Previews: PreviewProvider {
    static var previews: some View {
        MainView()
    }
}

//
//  ContentView.swift
//  textual_clock_companion
//
//  Created by Samuel Chassot on 08.02.23.
//

import SwiftUI
import CoreData

struct ContentView: View {
    @Environment(\.managedObjectContext) private var viewContext
    
    @State private var bgColor =
    Color(.sRGB, red: 0.98, green: 0.9, blue: 0.2)
    
    @State private var clockAddress = "raspberry"
    
    @State private var showSettings = false
    
    var body: some View {
        TabView{
            MainView()
                .tabItem{
                    Text("Home")
                    Image(systemName: "house")
                }.tag(1)
            SettingsView()
                .tabItem{
                    Text("Settings")
                    Image(systemName: "gear")
                }.tag(2)
        }
    }
   
    
   
}


struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView().environment(\.managedObjectContext, PersistenceController.preview.container.viewContext)
    }
}

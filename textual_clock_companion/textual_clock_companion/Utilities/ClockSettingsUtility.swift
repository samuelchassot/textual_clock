//
//  SettingsUtility.swift
//  textual_clock_companion
//
//  Created by Samuel Chassot on 08.02.23.
//

import Foundation
import CoreData

struct ClockSettingsUtility {
    static func getClockSettings(managedObjectContext: NSManagedObjectContext) -> ClockSettings?{
        let request = NSFetchRequest<NSFetchRequestResult>(entityName: "ClockSettings")
        //request.predicate = NSPredicate(format: "age = %@", "12")
        request.returnsObjectsAsFaults = false
        var resultClockSettings : ClockSettings? = nil
        do {
            var found = false
            let result = try managedObjectContext.fetch(request)
            for data in result as! [NSManagedObject] {
                if data.value(forKey: "id") as! Int16 == 0 {
                    resultClockSettings = data as? ClockSettings
                    found = true
                }
                break
            }
            if !found{
                //init the model to have one line
                let clockSettings = NSEntityDescription.insertNewObject(forEntityName: "ClockSettings", into: managedObjectContext) as! ClockSettings
                clockSettings.id = 0
                do{
                    try managedObjectContext.save()
                }catch{
                    print(error)
                }
                return getClockSettings(managedObjectContext: managedObjectContext)
            }

        } catch {

            print("Failed ClockSettings in ClockSettingsUtility")
        }
        return resultClockSettings
    }
    
    static func updateClockSettings(managedObjectContext: NSManagedObjectContext, newClockSettings: ClockSettings){
        let oldConfig = getClockSettings(managedObjectContext: managedObjectContext)!
        deleteClockSettings(managedObjectContext: managedObjectContext)
        let clockSettings = NSEntityDescription.insertNewObject(forEntityName: "ClockSettings", into: managedObjectContext) as! ClockSettings
        clockSettings.id = 0
        clockSettings.clock_name = newClockSettings.clock_name

        
        var ok = true
        do{
            try managedObjectContext.save()
        }catch{
            ok = false
        }
        if !ok {
            let newConfig = NSEntityDescription.insertNewObject(forEntityName: "ClockSettings", into: managedObjectContext) as! ClockSettings
            newConfig.id = 0
            newConfig.clock_name = oldConfig.clock_name
            
            do{
                try managedObjectContext.save()
            }catch{
                print(error)
            }
        }
        
    }
    
    /*
     Assumes that the values in the dict are correct
     */
    static func updateClockSettingsFromDicts(managedObjectContext: NSManagedObjectContext, newClockSettingsDictStringAttributes: Dictionary<ClockSettingsStringValues, String>) -> Bool{
        
        let oldClockSettings = getClockSettings(managedObjectContext: managedObjectContext)!
        deleteClockSettings(managedObjectContext: managedObjectContext)
        let clockSettings = NSEntityDescription.insertNewObject(forEntityName: "ClockSettings", into: managedObjectContext) as! ClockSettings
        clockSettings.id = 0
        clockSettings.clock_name = newClockSettingsDictStringAttributes[.clock_name]
        
        do{
            try managedObjectContext.save()
        }catch{
            updateClockSettings(managedObjectContext: managedObjectContext, newClockSettings: oldClockSettings)
            return false
        }
        return true
    }
    static func resetToDefault(managedObjectContext: NSManagedObjectContext){
        deleteClockSettings(managedObjectContext: managedObjectContext)
        _ = getClockSettings(managedObjectContext: managedObjectContext)
    }
    static func deleteClockSettings(managedObjectContext: NSManagedObjectContext){
        let clockSettings = ClockSettingsUtility.getClockSettings(managedObjectContext: managedObjectContext)
        if clockSettings != nil{
            //remove all objects
            let request = NSFetchRequest<NSFetchRequestResult>(entityName: "ClockSettings")
            //request.predicate = NSPredicate(format: "age = %@", "12")
            request.returnsObjectsAsFaults = false
            do {
                let result = try managedObjectContext.fetch(request)
                for data in result as! [NSManagedObject] {
                    managedObjectContext.delete(data)
                }
            } catch {
                print("Failed")
            }
        }
    }
}


enum ClockSettingsStringValues {
    case clock_name;
}

from motor_control import MotorController, MotorMovement

def main():
    # Using context manager for automatic cleanup
    with MotorController() as controller:
        movement = MotorMovement(controller)
        
        try:
            # Example movement sequence
            print("Moving forward...")
            movement.forward()
            
            print("Turning right...")
            movement.right()
            
            print("Moving backward...")
            movement.backward()
            
            print("Turning left...")
            movement.left()
            
        except KeyboardInterrupt:
            print("\nProgram interrupted by user")
            controller.emergency_stop()
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            controller.emergency_stop()

if __name__ == "__main__":
    main()

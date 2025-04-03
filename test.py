import project

def run_tests():
    # Test cases for R, even, and prime
    print("Test Cases for R, even, and prime:")
    print(f"RR(27, 3) is true: {project.test_RR(27, 3)}")
    print(f"RR(16, 20) is false: {project.test_RR(16, 20)}")
    print(f"EV_EN(14) is true: {project.test_even(14)}")
    print(f"EV_EN(13) is false: {project.test_even(13)}")
    print(f"PRIME(7) is true: {project.test_prime(7)}")
    print(f"PRIME(2) is false: {project.test_prime(2)}")
    
    # Test cases for RR2 (two-step reachability)
    print("\nTest Cases for RR2 (Two-step reachability):")
    print(f"RR2(27, 6) is true: {project.test_RR2(27, 6)}")
    print(f"RR2(27, 9) is false: {project.test_RR2(27, 9)}")
    
    # Test StatementA verification
    print(f"\nVerification of StatementA: {project.verify_statementA()}")

if __name__ == "__main__":
    run_tests()

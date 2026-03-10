#!/usr/bin/env python3
"""
Training script for the Isolation Forest anomaly detector
Generates synthetic network traffic data and trains the model
"""

import numpy as np
import pandas as pd
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from models.isolation_forest import AnomalyDetector
from core.feature_extractor import FeatureExtractor
from utils.logger import setup_logger

logger = setup_logger('train_model')

def generate_synthetic_training_data(n_samples=10000):
    """
    Generate synthetic network traffic data for training
    Returns feature matrix X and labels y (0=normal, 1=attack)
    """
    np.random.seed(42)
    
    # Initialize feature matrix
    X = np.zeros((n_samples, 13))
    y = np.zeros(n_samples)
    
    for i in range(n_samples):
        # Randomly decide if this is an attack sample (15% of data)
        is_attack = np.random.random() < 0.15
        y[i] = 1 if is_attack else 0
        
        # Generate features based on normal or attack traffic
        if is_attack:
            # Attack patterns
            attack_type = np.random.choice(['ddos', 'port_scan', 'syn_flood', 'brute_force', 'data_exfiltration'])
            
            if attack_type == 'ddos':
                # DDoS: high packet rate, small packets
                X[i, 0] = np.random.uniform(40, 200)  # packet_size
                X[i, 1] = np.random.uniform(0.0001, 0.001)  # inter_arrival_time
                X[i, 4] = np.random.uniform(500, 2000)  # packets_per_second
                X[i, 5] = X[i, 0] * X[i, 4]  # bytes_per_second
                X[i, 8] = 1  # flag_syn
                
            elif attack_type == 'port_scan':
                # Port scan: varying ports, SYN flags
                X[i, 0] = np.random.uniform(40, 80)
                X[i, 1] = np.random.uniform(0.01, 0.1)
                X[i, 2] = np.random.uniform(1, 65535)  # port_number
                X[i, 3] = 6  # protocol_encoded (TCP)
                X[i, 4] = np.random.uniform(100, 500)
                X[i, 8] = 1  # flag_syn
                
            elif attack_type == 'syn_flood':
                # SYN flood: many SYN flags, no ACK
                X[i, 0] = np.random.uniform(40, 100)
                X[i, 1] = np.random.uniform(0.0005, 0.005)
                X[i, 4] = np.random.uniform(300, 1000)
                X[i, 8] = 1  # flag_syn
                X[i, 9] = 0  # flag_ack
                
            elif attack_type == 'brute_force':
                # Brute force: repeated attempts to SSH/RDP
                X[i, 0] = np.random.uniform(60, 150)
                X[i, 1] = np.random.uniform(0.1, 0.5)
                X[i, 2] = np.random.choice([22, 3389])  # port_number
                X[i, 4] = np.random.uniform(1, 5)
                X[i, 6] = np.random.randint(1024, 65535)  # src_port
                X[i, 7] = X[i, 2]  # dst_port
                
            else:  # data_exfiltration
                # Data exfiltration: large packets, unusual ports
                X[i, 0] = np.random.uniform(1000, 65000)
                X[i, 1] = np.random.uniform(0.5, 5)
                X[i, 2] = np.random.choice([53, 123, 443, 8080])
                X[i, 4] = np.random.uniform(0.1, 2)
                X[i, 5] = X[i, 0] * X[i, 4]
        else:
            # Normal traffic patterns
            X[i, 0] = np.random.uniform(40, 1500)  # packet_size
            X[i, 1] = np.random.uniform(0.001, 0.1)  # inter_arrival_time
            X[i, 2] = np.random.choice([80, 443, 53, 22, 3389, 8080])  # port_number
            X[i, 3] = np.random.choice([6, 17])  # protocol_encoded (TCP/UDP)
            X[i, 4] = np.random.uniform(1, 100)  # packets_per_second
            X[i, 5] = X[i, 0] * X[i, 4]  # bytes_per_second
            X[i, 6] = np.random.randint(1024, 65535)  # src_port
            X[i, 7] = X[i, 2]  # dst_port
            
            # Flags (normal TCP traffic has mixed flags)
            X[i, 8] = np.random.choice([0, 1], p=[0.7, 0.3])  # flag_syn
            X[i, 9] = np.random.choice([0, 1], p=[0.3, 0.7])  # flag_ack
            X[i, 10] = np.random.choice([0, 1], p=[0.9, 0.1])  # flag_fin
            X[i, 11] = np.random.choice([0, 1], p=[0.95, 0.05])  # flag_rst
            X[i, 12] = np.random.uniform(0.001, 1)  # connection_duration
    
    # Normalize some features
    X[:, 0] = X[:, 0] / 65535  # Normalize packet size
    X[:, 4] = np.log1p(X[:, 4]) / 10  # Log transform packets_per_second
    X[:, 5] = np.log1p(X[:, 5]) / 20  # Log transform bytes_per_second
    X[:, 12] = X[:, 12] / 10  # Normalize duration
    
    return X, y

def main():
    """Main training function"""
    logger.info("Starting model training...")
    
    # Generate training data
    logger.info("Generating synthetic training data...")
    X, y = generate_synthetic_training_data(10000)
    
    # Initialize and train detector
    logger.info("Initializing AnomalyDetector...")
    detector = AnomalyDetector(contamination=0.15, n_estimators=100)
    
    logger.info("Training model...")
    detector.train(X)
    
    # Test on some samples
    test_idx = np.random.choice(len(X), 100, replace=False)
    X_test = X[test_idx]
    y_test = y[test_idx]
    
    correct = 0
    for i, (features, true_label) in enumerate(zip(X_test, y_test)):
        pred = detector.predict(features.reshape(1, -1))
        pred_label = 1 if pred['is_anomaly'] else 0
        if pred_label == true_label:
            correct += 1
    
    accuracy = correct / len(X_test)
    logger.info(f"Test accuracy: {accuracy:.2%}")
    
    # Save model
    model_path = Path(__file__).parent / 'detector.pkl'
    detector.save(str(model_path))
    logger.info(f"Model saved to {model_path}")
    
    # Print model info
    logger.info("=" * 50)
    logger.info("Model Training Complete")
    logger.info(f"Contamination: {detector.contamination}")
    logger.info(f"Number of estimators: {detector.n_estimators}")
    logger.info(f"Training samples: {X.shape[0]}")
    logger.info(f"Test accuracy: {accuracy:.2%}")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()

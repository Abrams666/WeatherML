//import
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>

//config
const int row = 3812;
const int col = 32;
const int maxTrainTime = 1000000;
const float learnRate = 0.00001;
const float testSetRatio = 0.2;
const char dataPath[100] = "../../data/data467050_std.csv";
const char weightPath[100] = "../../data/weight.csv";

//value
const int testSetNum = row * testSetRatio;
const int trainSetNum = row - testSetNum;

//function
double dot(double* a, float* b, int len){
	double total = 0;

	for (int i = 0; i < len; i++) {
		total += a[i] * b[i];
	}

	return total;
}

double cost(double *w, float **x, int setNum){
	double totalCost = 0;

	for (int i = 0; i < setNum - 1; i++) {
		totalCost += (dot(w, x[i], col) - x[i + 1][col - 1]) * (dot(w, x[i], col) - x[i + 1][col - 1]);
	}

	return totalCost;
}

double PartialDerivative(double *w, float *x, float *x2, int idx){
	return 2 * (dot(w, x, col) - x2[col-1]) * x[idx];
}

//run
int main() {
	//value
	float** trainSet = (float **)malloc(trainSetNum * sizeof(float*));
	for (int i = 0; i < trainSetNum; i++) {
		trainSet[i] = (float *)malloc((col) * sizeof(float));
	}
	float** testSet = (float**)malloc(testSetNum * sizeof(float*));
	for (int i = 0; i < testSetNum; i++) {
		testSet[i] = (float*)malloc((col) * sizeof(float));
	}
	float id = 0;

	//read file
	FILE* dataFile;

	if ((dataFile = fopen(dataPath, "r")) == NULL) {
		printf("File could not be opened\n");
		return 0;
	}

	//remove header
	char header[2000] = "";
	fscanf(dataFile, "%[^\n]\n", header);

	//printf("Reading and set trainSet...\n");
	for (int i = 0; i < trainSetNum; i++) {
		for (int j = 0; j < col; j++) {
			if(j==col-1){
				fscanf(dataFile, "%f\n", &trainSet[i][j]);
				//printf("%.2f,", trainSet[i][j]);
			}
			else {
				fscanf(dataFile, "%f,", &trainSet[i][j]);
				//printf("%.2f,", trainSet[i][j]);
			}
		}
		//printf("\n");
	}

	//printf("Reading and set testSet...\n");
	for (int i = 0; i < testSetNum; i++) {
		for (int j = 0; j < col; j++) {
			if (j == col - 1) {
				fscanf(dataFile, "%f\n", &testSet[i][j]);
				//printf("%.2f,", testSet[i][j]);
			}
			else {
				fscanf(dataFile, "%f,", &testSet[i][j]);
				//printf("%.2f,", testSet[i][j]);
			}
		}
		//printf("\n");
	}

	fclose(dataFile);

	//printf("trainSet:\n");
	//for (int i = 0; i < trainSetNum; i++) {
	//	for (int j = 0; j < col; j++) {
	//			printf("%.2f,", trainSet[i][j]);
	//	}
	//	printf("\n");
	//}

	//printf("testSet:\n");
	//for (int i = 0; i < testSetNum; i++) {
	//	for (int j = 0; j < col; j++) {
	//		printf("%.2f,", testSet[i][j]);
	//	}
	//	printf("\n");
	//}

	//train
	//system("PAUSE");
	printf("Start training...\n");

	double bestCost = 1001;
	double currentCost = 1001;
	int count = 0;
	double* weight = (double*)malloc(col * sizeof(double));
	double* bestWeight = (double*)malloc(col * sizeof(double));
	for (int i = 0; i < col; i++) {
		weight[i] = 1;
		bestWeight[i] = 1;
	}

	while (bestCost > 1000 && count < maxTrainTime) {
		for (int i = 0; i < trainSetNum - 1 && count < maxTrainTime; i++) {
			count++;

			//record
			currentCost = cost(weight, testSet, testSetNum);
			printf("ID:%5d, cost:%10f\n", count, currentCost);
			if (count == 1) {
				bestCost = currentCost;
				for (int j = 0; j < col; j++) {
					bestWeight[j] = weight[j];
				}
				//printf("ID:%5d, cost:%10f\n", count, currentCost);
			}
			else {
				if (currentCost < bestCost) {
					printf("----------\nBest Weight Updated\n");
					//printf("ID:%5d, cost:%10f\n", count, currentCost);
					bestCost = currentCost;
					for (int j = 0; j < col; j++) {
						bestWeight[j] = weight[j];
					}
					for (int k = 0; k < col; k++) {
						//printf("%f,",weight[k]);
					}
					printf("\n----------\n");
				}
			}


			for (int j = 0; j < col; j++) {
				weight[j] -= learnRate * PartialDerivative(weight, trainSet[i],trainSet[i+1], j);
				//printf("Index:%5d, gradient:%10f\n", j, gradient(weight, trainSet[i], trainSet[i + 1], j));
			}
		}
	}

	printf("----------\nCurrent Best Weight\n");
	printf("Lowest cost:%10f\n", bestCost);

	FILE* weightFile;
	weightFile = fopen(weightPath, "w");
	fprintf(weightFile, "StnPres,SeaPres,StnPresMax,StnPresMin,Temperature,T Max,T Min,Td dew point,RH,RHMin,WS,WD,WSGust,WDGust,PrecpHour,PrecpMax10,PrecpMax60,SunShine,SunshineRate,GloblRad,VisbMean,EvapA,UVI Max,Cloud Amount,TxSoil0cm,TxSoil5cm,TxSoil10cm,TxSoil20cm,TxSoil30cm,TxSoil50cm,TxSoil100cm,Precp,\n");

	for (int k = 0; k < col; k++) {
		printf("%f,", weight[k]);
		fprintf(weightFile, "%f,", weight[k]);
	}
	printf("\n----------\n");

	//end
	fclose(weightFile);
	return 0;
	system("PAUSE");
}
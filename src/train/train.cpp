//import
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdlib.h>

//config
const int trainSetNum = 2848;
const int testSetNum = 713;
const int col = 31;
const int maxTrainTime = 1000000;
const int printPerTime = 1;
const float learnRate = 0.00001;

const char trainSetDataPath[100] = "../../data/trainSetDataFile467050_std.csv";
const char trainSetRainDataPath[100] = "../../data/trainSetRainDataFile467050_std.csv";
const char testSetDataPath[100] = "../../data/testSetDataFile467050_std.csv";
const char testSetRainDataPath[100] = "../../data/testSetRainDataFile467050_std.csv";
const char weightPath[100] = "../../data/weight.csv";

//function
double dot(double* a, float* b, int len){
	double total = 0;

	for (int i = 0; i < len; i++) {
		total += a[i] * b[i];
	}

	return total;
}

double cost(double *w, float **x, float *y, int setNum){
	double totalCost = 0;

	for (int i = 0; i < setNum - 1; i++) {
		totalCost += (dot(w, x[i], col) - y[i]) * (dot(w, x[i], col) - y[i]);
	}

	return totalCost;
}

double PartialDerivative(double *w, float *x, float y, int idx){
	return 2 * (dot(w, x, col) - y) * x[idx];
}

//run
int main() {
	//value
	float** trainSet = (float**)malloc(trainSetNum * sizeof(float*));
	for (int i = 0; i < trainSetNum; i++) {
		trainSet[i] = (float*)malloc((col) * sizeof(float));
	}

	float* trainSetRain = (float *)malloc(trainSetNum * sizeof(float));

	float** testSet = (float**)malloc(testSetNum * sizeof(float*));
	for (int i = 0; i < testSetNum; i++) {
		testSet[i] = (float*)malloc((col) * sizeof(float));
	}

	float* testSetRain = (float*)malloc(testSetNum * sizeof(float));

	float id = 0;

	//read file
	FILE* dataFile;
	FILE* rainDataFile;

	if ((dataFile = fopen(trainSetDataPath, "r")) == NULL) {
		printf("File could not be opened\n");
		return 0;
	}

	if ((rainDataFile = fopen(trainSetRainDataPath, "r")) == NULL) {
		printf("File could not be opened\n");
		return 0;
	}

	//remove header
	char header[2000] = "";
	fscanf(rainDataFile, "%[^\n]\n", header);
	fscanf(dataFile, "%[^\n]\n", header);

	for (int i = 0; i < trainSetNum; i++) {
		for (int j = 0; j < col; j++) {
			if(j==col-1){
				fscanf(dataFile, "%f\n", &trainSet[i][j]);
			}
			else {
				fscanf(dataFile, "%f,", &trainSet[i][j]);
			}
		}

		fscanf(rainDataFile, "%f\n", &trainSetRain[i]);
	}

	if ((dataFile = fopen(testSetDataPath, "r")) == NULL) {
		printf("File could not be opened\n");
		return 0;
	}

	if ((rainDataFile = fopen(testSetRainDataPath, "r")) == NULL) {
		printf("File could not be opened\n");
		return 0;
	}

	//remove header
	fscanf(rainDataFile, "%[^\n]\n", header);
	fscanf(dataFile, "%[^\n]\n", header);

	for (int i = 0; i < testSetNum; i++) {
		for (int j = 0; j < col; j++) {
			if (j == col - 1) {
				fscanf(dataFile, "%f\n", &testSet[i][j]);
			}
			else {
				fscanf(dataFile, "%f,", &testSet[i][j]);
			}
		}

		fscanf(rainDataFile, "%f\n", &testSetRain[i]);
	}

	fclose(dataFile);
	fclose(rainDataFile);

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

	while (bestCost > 100 && count < maxTrainTime) {
		for (int i = 0; i < trainSetNum && count < maxTrainTime; i++) {
			count++;

			//record
			currentCost = cost(weight, testSet, testSetRain, testSetNum);
			if (count % printPerTime == 0) {
				printf("ID:%5d, cost:%10f\n", count, currentCost);
			}
			if (count == 1) {
				bestCost = currentCost;
				for (int j = 0; j < col; j++) {
					bestWeight[j] = weight[j];
				}
			}
			else {
				if (currentCost < bestCost) {
					printf("----------\nBest Weight Updated\n");
					bestCost = currentCost;
					for (int j = 0; j < col; j++) {
						bestWeight[j] = weight[j];
					}
					printf("\n----------\n");
				}
			}


			for (int j = 0; j < col; j++) {
				weight[j] -= learnRate * PartialDerivative(weight, trainSet[i], trainSetRain[i], j);
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
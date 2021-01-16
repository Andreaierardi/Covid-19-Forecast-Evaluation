function [test, cv, reject] = dm_fsa_cv(d, wceband, wpeband)

% This function performs the tests for equal predictive accuracy using 
% fixed-smoothing asymptotics, as in Laura Coroneoy and Fabrizio Iacone,
% "Comparing predictive accuracy in small samples using fixed-smoothing 
% asymptotics", Journal of Applied Econometrics, forthcoming.

% INPUTS: 
% d         loss differential (T x 1)
% wceband   bandwidth for Weighted Covariance Estimate (default = T^(1/2))
% wpeband   bandwidth for Weighted Periodogram Estimate (default = T^(1/3))


% OUTPUTS: 

% test     2x1 array with test statistic values: 
%            1) Test statistic with Weighted Covariance Estimate and Bartlett kernel
%            2) Test statistic with Weighted Periodogram Estimate and Daniell kernel

% cv        2x3 array with the 20%, 10% and 5% critical values for the:
%            1) Fixed-b test
%            2) Fixed-m test

test = NaN(2,1);
cv = NaN(2,3);

T = size(d, 1);

%mean(d)

num = sqrt(T)* mean(d);

num


%% Fixed-b test using Weighted Covariance Estimate and Bartlett kernel

if exist ('wceband', 'var') == 0
    wceband = floor(T^(1/2));
end

WCEb = NeweyWest(d,wceband,1);
num/WCEb 
test(1) = num / sqrt(WCEb);

b = wceband/T;

CV_WCE_b_97 = 1.9600 + 2.9694*b + 0.4160*b^2 - 0.5324*b^3; 
CV_WCE_b_95 = 1.6449 + 2.1859*b + 0.3142*b^2 - 0.3427*b^3; 
CV_WCE_b_90 = 1.2816 + 1.3040*b + 0.5135*b^2 - 0.3386*b^3;

cv(1,:) = [CV_WCE_b_90 CV_WCE_b_95 CV_WCE_b_97];

%% Fixed-m test using Weighted Periodogram Estimate and Daniell kernel

if exist('wpeband', 'var') == 0
    wpeband = floor(T^(1/3));
end

AA = dftmtx(T);
w = AA*d; % discrete fourier transform of d
pdm = w.* conj(w)/ (2*pi*T);
WPE = sum(pdm(2:wpeband+1,:))/wpeband * 2*pi;

test(2) = num / sqrt(WPE);

cv(2,:) = [icdf('t',[0.90],2*wpeband) icdf('t',[0.95],2*wpeband) icdf('t',[0.975],2*wpeband)];

%% significance

%% Results
    
ind10 = 10*(abs(test) > abs(cv(:,2)));
ind5  =  5*(abs(test) > abs(cv(:,3)));
    
reject = ind10-ind5;

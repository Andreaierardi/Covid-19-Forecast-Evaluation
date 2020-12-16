function [bsdata, index]= bootstrap(data,B,w)

% INPUTS:
%     data  - T by 1 vector of data to be bootstrapped
%     b     - Number of bootstraps
%     w     - Max block length


% OUTPUTS:
%     BSDATA  - T x B matrix of bootstrapped data
%     INDEX   - T by B matrix of locations of the original BSDATA=DATA(indexes);

n = size(data,1);
ind = (1:n)';
DATA = [ind; ind; ind];
data_ = [data; data; data];
index = zeros(n,B);
for i=1:B
    data_st =[]; 
    r=0;
    while r < n
        L = randi(w,1);
        U = randi(n,1);
        data_st = [data_st; DATA(U:U+L-1)];
        r = length(data_st);
    end
    index(:,i) = data_st(1:n);
    bsdata(:,i) = data_(index(:,i),:);
end



